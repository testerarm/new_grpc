from __future__ import unicode_literals

import logging
import os

#from opensfm import dataset
from opensfm import transformations as tf
from opensfm import io
from opensfm import types
from six import iteritems

import opensfm_interface

logger = logging.getLogger(__name__)


class VisualSFMCommand:
    name = 'export_visualsfm'
    help = "Export reconstruction to NVM_V3 format from VisualSfM"

    def add_arguments(self, parser):
        parser.add_argument('dataset', help='dataset to process')
        parser.add_argument('--points',
                            action='store_true',
                            help='export points')
        parser.add_argument('--image_list',
                            type=str,
                            help='Export only the shots included in this file (path to .txt file)')

    def run(self, file_path, opensfm_config, image_list=None):
        #data = dataset.DataSet(args.dataset)
        udata = opensfm_interface.UndistortedDataSet(file_path, opensfm_config, 'undistorted')
        points = True
        reconstructions = udata.load_undistorted_reconstruction()
        graph = udata.load_undistorted_tracks_graph()

        export_only = None
        if image_list:
            export_only = {}
            with open(image_list, 'r') as f:
                for image in f:
                    export_only[image.strip()] = True

        if reconstructions:
            self.export(reconstructions[0], graph, udata, points, export_only)

    def export(self, reconstruction, graph, udata, with_points, export_only):
        lines = ['NVM_V3', '', len(reconstruction.shots)]
        shot_size_cache = {}
        shot_index = {}
        i = 0
        skipped_shots = 0

        for shot in reconstruction.shots.values():
            if export_only is not None and not shot.id in export_only:
                skipped_shots += 1
                continue

            q = tf.quaternion_from_matrix(shot.pose.get_rotation_matrix())
            o = shot.pose.get_origin()

            shot_size_cache[shot.id] = udata.undistorted_image_size(shot.id)
            shot_index[shot.id] = i
            i += 1

            if type(shot.camera) == types.BrownPerspectiveCamera:
                # Will approximate Brown model, not optimal
                focal_normalized = shot.camera.focal_x
            else:
                focal_normalized = shot.camera.focal

            words = [
                self.image_path(shot.id, udata),
                focal_normalized * max(shot_size_cache[shot.id]),
                q[0], q[1], q[2], q[3],
                o[0], o[1], o[2],
                '0', '0',
            ]
            lines.append(' '.join(map(str, words)))
        
        # Adjust shots count
        lines[2] = str(lines[2] - skipped_shots)

        if with_points:
            skipped_points = 0
            lines.append('')
            points = reconstruction.points
            lines.append(len(points))
            points_count_index = len(lines) - 1

            for point_id, point in iteritems(points):
                shots = reconstruction.shots
                coord = point.coordinates
                color = list(map(int, point.color))

                view_list = graph[point_id]
                view_line = []

                for shot_key, view in iteritems(view_list):
                    if export_only is not None and not shot_key in export_only:
                        continue

                    if shot_key in shots.keys():
                        v = view['feature']
                        x = (0.5 + v[0]) * shot_size_cache[shot_key][1]
                        y = (0.5 + v[1]) * shot_size_cache[shot_key][0]
                        view_line.append(' '.join(
                            map(str, [shot_index[shot_key], view['feature_id'], x, y])))
                
                if len(view_line) > 1:
                    lines.append(' '.join(map(str, coord)) + ' ' + 
                                ' '.join(map(str, color)) + ' ' + 
                                str(len(view_line)) + ' ' + ' '.join(view_line))
                else:
                    skipped_points += 1
            
            # Adjust points count
            lines[points_count_index] = str(lines[points_count_index] - skipped_points)
        else:
            lines += ['0', '']

        lines += ['0', '', '0']

        with io.open_wt(udata.data_path + '/reconstruction.nvm') as fout:
            fout.write('\n'.join(lines))

    def image_path(self, image, udata):
        """Path to the undistorted image relative to the dataset path."""
        path = udata._undistorted_image_file(image)
        return os.path.relpath(path, udata.data_path)

import opensfm_interface
from opensfm.large import tools
import numpy as np
from opensfm import io
import os
import os.path



def _clusters_path(file_path):
    return os.path.join(file_path, 'cluster.npz')

# def _submodels_path(file_path):
#         return os.path.join(file_path, self.config['submodels_relpath'])



def save_clusters(file_path, images, positions, labels, centers):
        filepath = _clusters_path(file_path)
        np.savez_compressed(
            filepath,
            images=images,
            positions=positions,
            labels=labels,
            centers=centers)

def save_clusters_with_neighbors(file_path, clusters):
        filepath = _clusters_with_neighbors_path(file_path)
        np.savez_compressed(
            filepath,
            clusters=clusters)

def load_clusters(file_path):
        c = np.load(_clusters_path(file_path), allow_pickle=True)
        images = c['images'].ravel()
        labels = c['labels'].ravel()
        return images, c['positions'], labels, c['centers']

def _image_list_path(file_path):
        return os.path.join(file_path, 'image_list_with_gps.tsv')


def _clusters_path(file_path):
        return os.path.join(file_path, 'clusters.npz')

def _clusters_with_neighbors_path(file_path):
        return os.path.join(file_path, 'clusters_with_neighbors.npz')


def images_with_gps(file_path):
        with io.open_rt(_image_list_path(file_path)) as csvfile:
            for line in csvfile:
                image, lat, lon = line.split(u'\t')
                yield image, float(lat), float(lon)


def load_clusters(file_path):
    c = np.load(_clusters_path(file_path), allow_pickle=True)
    images = c['images'].ravel()
    labels = c['labels'].ravel()
    return images, c['positions'], labels, c['centers']

def save_clusters_with_neighbors(file_path, clusters):
    filepath = _clusters_with_neighbors_path(file_path)
    np.savez_compressed(
        filepath,
        clusters=clusters)

def load_clusters_with_neighbors(file_path):
    c = np.load(_clusters_with_neighbors_path(file_path), allow_pickle=True)
    #print(c)
    return c['clusters']


def _create_image_list(ref_images, image_list_path):
        #create image list with coordinate of gps points
        ills = []
        for image in ref_images:
            exif = opensfm_interface.load_exif(image_list_path+'/',image)
            if ('gps' not in exif or
                    'latitude' not in exif['gps'] or
                    'longitude' not in exif['gps']):
                logger.warning(
                    'Skipping {} because of missing GPS'.format(image))
                continue

            lat = exif['gps']['latitude']
            lon = exif['gps']['longitude']
            ills.append((image, lat, lon))
        #print(ills)
        create_image_list(ills, image_list_path)


def create_image_list(ills, file_path):
    with io.open_wt(_image_list_path(file_path)) as csvfile:
        for image, lat, lon in ills:
            csvfile.write(u'{}\t{}\t{}\n'.format(image, lat, lon))


def _cluster_images(cluster_size, file_path):
        images = []
        positions = []
        #print("in cluster images")
        #print("cluster size: " + str(cluster_size))
        for image, lat, lon in images_with_gps(file_path):
            images.append(image)
            positions.append([lat, lon])

        positions = np.array(positions, np.float32)
        images = np.array(images).reshape((len(images), 1))
        #print('images')
        #print(images)
        #print('positions')
        #print(positions)

        #print(images.shape)

        K = float(images.shape[0]) / cluster_size
        K = int(np.ceil(K))
        #print('K')
        #print(K)
        #print('labels')

        labels, centers = tools.kmeans(positions, K)[1:]
        #print(labels)
        #print(centers)

        images = images.ravel()

        #print(images)
        labels = labels.ravel()
        #print(labels)

        save_clusters(file_path,images, positions, labels, centers)

def _add_cluster_neighbors(file_path,  max_distance):
        images, positions, labels, centers = load_clusters(file_path)
        clusters = tools.add_cluster_neighbors(
            positions, labels, centers, max_distance)

        image_clusters = []
        for cluster in clusters:
            image_clusters.append(list(np.take(images, np.array(cluster))))

        save_clusters_with_neighbors(file_path, image_clusters)


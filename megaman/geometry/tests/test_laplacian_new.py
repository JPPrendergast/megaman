import os

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from scipy.sparse import isspmatrix, csr_matrix
from scipy import io

from megaman.geometry.adjacency_new import compute_adjacency_matrix
from megaman.geometry.affinity_new import compute_affinity_matrix
from megaman.geometry.laplacian_new import Laplacian, compute_laplacian_matrix


TEST_DATA = os.path.join(os.path.dirname(__file__),
                        'testmegaman_laplacian_rad0_2_lam1_5_n200.mat')


def test_laplacian_vs_matlab():
    # Test that the laplacian calculation matches the matlab result
    matlab = io.loadmat(TEST_DATA)

    laplacians = {'unnormalized': matlab['Lunnorm'],
                  'symmetricnormalized': matlab['Lsymnorm'],
                  'geometric': matlab['Lgeom'],
                  'randomwalk': matlab['Lrw'],
                  'renormalized': matlab['Lreno1_5']}

    radius = matlab['rad'][0]

    def check_laplacian(input_type, laplacian_method):
        kwargs = {'scaling_epps': radius}
        if laplacian_method == 'renormalized':
            kwargs['renormalization_exponent'] = 1.5
        adjacency = input_type(np.sqrt(matlab['S']))
        affinity = compute_affinity_matrix(adjacency, radius=radius)
        laplacian = compute_laplacian_matrix(affinity,
                                             method=laplacian_method,
                                             **kwargs)
        if input_type is csr_matrix:
            laplacian = laplacian.toarray()
        assert_allclose(laplacian, laplacians[laplacian_method])

    for input_type in [np.array, csr_matrix]:
        for laplacian_method in laplacians:
            yield check_laplacian, input_type, laplacian_method


def test_laplacian_smoketest():
    rand = np.random.RandomState(42)
    X = rand.rand(20, 2)
    adj = compute_adjacency_matrix(X, radius=0.5)
    aff = compute_affinity_matrix(adj, radius=0.1)

    def check_laplacian(method):
        lap = compute_laplacian_matrix(aff, method=method)

        assert isspmatrix(lap)
        assert_equal(lap.shape, (X.shape[0], X.shape[0]))

    for method in Laplacian.asymmetric_methods():
        yield check_laplacian, method


def test_laplacian_full_output():
    # Test that full_output symmetrized laplacians have the right form
    rand = np.random.RandomState(42)
    X = rand.rand(20, 2)

    def check_symmetric(method, adjacency_radius, affinity_radius):
        adj = compute_adjacency_matrix(X, radius=adjacency_radius)
        aff = compute_affinity_matrix(adj, radius=affinity_radius)
        lap, lapsym, w = compute_laplacian_matrix(aff, method=method,
                                                  full_output=True)

        sym = w[:, np.newaxis] * (lap.toarray() + np.eye(*lap.shape))

        assert_allclose(lapsym.toarray(), sym)

    for method in Laplacian.asymmetric_methods():
        for adjacency_radius in [0.5, 1.0]:
            for affinity_radius in [0.1, 0.3]:
                yield check_symmetric, method, adjacency_radius, affinity_radius

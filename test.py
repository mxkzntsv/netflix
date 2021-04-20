import numpy as np
import em
import common
from common import GaussianMixture
from scipy.stats import multivariate_normal as MN
from scipy.stats import norm as N
from numpy.linalg import norm


X = np.loadtxt("test_incomplete.txt")
X_gold = np.loadtxt("test_complete.txt")

K = 4
n, d = X.shape
seed = 0

def testing_estep():
    X = np.array(
        [[0.85794562, 0.84725174],
        [0.6235637 , 0.38438171],
        [0.29753461, 0.05671298],
        [0.27265629, 0.47766512],
        [0.81216873, 0.47997717],
        [0.3927848 , 0.83607876],
        [0.33739616, 0.64817187],
        [0.36824154, 0.95715516],
        [0.14035078, 0.87008726],
        [0.47360805, 0.80091075],
        [0.52047748, 0.67887953],
        [0.72063265, 0.58201979],
        [0.53737323, 0.75861562],
        [0.10590761, 0.47360042],
        [0.18633234, 0.73691818]]
    )

    mu = np.array(
        [[0.6235637 , 0.38438171],
        [0.3927848 , 0.83607876],
        [0.81216873, 0.47997717],
        [0.14035078, 0.87008726],
        [0.36824154, 0.95715516],
        [0.10590761, 0.47360042]]
    )

    K = 6

    var = np.array([0.10038354, 0.07227467, 0.13240693, 0.12411825, 0.10497521, 0.12220856])
    p = np.array([0.1680912, 0.15835331, 0.21384187, 0.14223565, 0.14295074, 0.17452722])

    print(f'X shape: {X.shape}')
    print(f'mu shape: {mu.shape}')
    print(f'var shape: {var.shape}')
    print(f'p shape: {p.shape}\n')


    def estep(X, mixture):
        K, _ = mixture.mu.shape
        n, d = X.shape
        gprob = lambda x, m, s: (1 / (2*np.pi*s)**(d/2)) * (np.exp(-((x-m)**2).sum(axis=1) / (2*s)))
        soft_counts, ll_ = np.empty((0,K)), np.empty((0,K))

        for i in range(n):
            prob = gprob(np.tile(X[i], (K,1)), mixture.mu, mixture.var)
            # import pdb; pdb.set_trace()
            prob_ll = prob.reshape(1, K)
            prob_post = (prob*mixture.p)/(prob*mixture.p).sum()
            soft_counts = np.append(soft_counts, prob_post, axis=0)
            ll_ =  np.append(ll_, prob_ll, axis=0)
        ll = np.log((ll_*mixture.p).sum(axis=1)).sum()

        return soft_counts, ll

    def main():
        mx = GaussianMixture(mu=mu, var=var, p=p)
        soft_counts, ll = estep(X, mx)
        print(soft_counts)
        print(f"\n{ll}\n")



    main()


def testing_mstep():
    X = np.array(
       [[0.8579456, 0.8472517],
        [0.6235637, 0.3843817],
        [0.2975346, 0.056713 ],
        [0.2726563, 0.4776651],
        [0.8121687, 0.4799772],
        [0.3927848, 0.8360788],
        [0.3373962, 0.6481719],
        [0.3682415, 0.9571552],
        [0.1403508, 0.8700873],
        [0.4736081, 0.8009108],
        [0.5204775, 0.6788795],
        [0.7206326, 0.5820198],
        [0.5373732, 0.7586156],
        [0.1059076, 0.4736004],
        [0.1863323, 0.7369182]]
    )
    K = 6
    post = np.array(
      [[0.1576507, 0.2054434, 0.1731482, 0.1565217, 0.121698 , 0.1855379],
       [0.1094766, 0.2231059, 0.2410914, 0.0959303, 0.1980756, 0.1323202],
       [0.2267965, 0.3695521, 0.0283617, 0.0347871, 0.0080724, 0.3324303],
       [0.1667019, 0.1863798, 0.2096461, 0.171201 , 0.0988612, 0.1672101],
       [0.0425031, 0.2299618, 0.0515154, 0.3394759, 0.1875312, 0.1490127],
       [0.0979909, 0.2867746, 0.1689572, 0.2105468, 0.0069597, 0.2287709],
       [0.1676452, 0.1689703, 0.2584805, 0.1867419, 0.0984646, 0.1196975],
       [0.2865521, 0.0247376, 0.2738745, 0.2754646, 0.0864147, 0.0529565],
       [0.1135306, 0.1309086, 0.2052281, 0.1578637, 0.3557405, 0.0367285],
       [0.1051046, 0.0811693, 0.3286373, 0.1274537, 0.2346427, 0.1229924],
       [0.0975773, 0.0677495, 0.4028626, 0.0848183, 0.1206645, 0.2263277],
       [0.2489934, 0.0294492, 0.2541346, 0.029145 , 0.2961437, 0.142134 ],
       [0.3535068, 0.2189041, 0.2675523, 0.0141827, 0.1023528, 0.0435012],
       [0.1555576, 0.0623657, 0.1670313, 0.2176055, 0.0336956, 0.3637442],
       [0.1917808, 0.0898279, 0.1771067, 0.0317966, 0.1949439, 0.3145441]]
    )

    def mstep(X: np.ndarray, post: np.ndarray) -> GaussianMixture:

        nrow, ncol = X.shape
        nom_ = np.dot(post.T, X)
        up_mu = np.zeros(nom_.shape)  # Initialize updates of mu
        up_var = np.zeros(nom_.shape[0])  # Initialize updates of var
        up_p = 1/nrow * post.sum(axis=0)  # Updates of p

        for i, val in enumerate(nom_):
            up_mu[i] = val / post.sum(axis=0)[i]
            temp = 0
            # import pdb; pdb.set_trace()
            for j in range(nrow):
                temp += post.T[i] * norm(X[j] - up_mu[i])**2 
            import pdb; pdb.set_trace()
            up_var[i] = temp.sum() / (post.sum() * ncol)

        return GaussianMixture(mu=up_mu, var=up_var, p=up_p)



    def main():
        mixture = mstep(X, post)
        print(mixture)

    main()


if __name__=="__main__":
    testing_mstep()
"""
This file demonstrates training a Gaussian Process with derivative observations.
"""
import time

import numpy as np
import matplotlib.pyplot as plt

import gpflow



def func1(x):
    f = np.sin(12*x) + 0.66*np.cos(25*x)
    deriv = 12 * np.cos(12*x) - 0.66 * 25 * np.sin(25*x)  # the analytical deriv
    return f, deriv


def plot(m, xx, x_data, y_data):
    plt.figure(figsize=(12, 6))


    if xx.shape[1] == 2:
        plt.plot(xx[:, 0], func1(xx[:, 0])[0], 'g', lw=4)
    else:
        plt.plot(xx, func1(xx)[0], 'g', lw=4)

    plt.plot(x_data, y_data, 'kx', mew=2)

    time_before = time.time()
    if xx.shape[1] == 2:
        mean, var = m.predict_y(xx)

        ax = plt.gca()

        derivative_obs = x_data

        f, derivs = func1(derivative_obs)
        for loc, f, der in zip(derivative_obs, f, derivs):
            dx = 0.05
            ax.arrow(loc[0], f[0], dx, der[0] * dx)
        xx = xx[:, 0:1]

    else:
        mean, var = m.predict_y(xx)
    print("Time making predictions is {}".format(time.time()-time_before))


    plt.plot(xx, mean, 'b', lw=2)
    plt.fill_between(xx[:,0], mean[:,0] - 2*np.sqrt(var[:,0]), mean[:,0] + 2*np.sqrt(var[:,0]), color='blue', alpha=0.2)
    plt.xlim(-0.1, 1.1)





def main():

    rng = np.random.RandomState(100)

    num_obs = 10
    x_data = rng.rand(num_obs,1)
    x_axis = np.linspace(x_data.min()-0.2, x_data.max()+0.2, 50)[:, None]
    f_data, derivs = func1(x_data)

    #plt.plot(x_axis, func1(x_axis)[0], 'g', lw=4)
    #plt.plot(x_axis, func1(x_axis)[1], 'b', lw=4)
    #plt.show()



    x_full = np.concatenate((x_data, x_data), axis=0)
    x_full = np.concatenate((x_full[:, :], np.zeros_like(x_full)[:, :]), axis=1)
    x_full[-derivs.size:, 1] = 1
    f_full = np.concatenate((f_data, derivs), axis=0)

    rbf_kernel = gpflow.kernels.RBF(1)
    rbf_kernel2 = gpflow.kernels.RBF(1)
    rbf_kernel3 = gpflow.kernels.RBF(1)
    deriv_kernel = gpflow.derivative_kernel.DifferentialObservationsKernelDynamic(1, rbf_kernel2, 1)
    deriv_kernel2 = gpflow.derivative_kernel.DifferentialObservationsKernelDynamic(1, rbf_kernel3, 1)
    deriv_kernel3 = gpflow.derivative_kernel.RBFDerivativeKern(1, 1)

    model_no_derivs = gpflow.gpr.GPR(x_data, f_data, kern=rbf_kernel)
    model_no_derivs.likelihood.variance = 1e-3
    model_no_derivs.likelihood.variance.fixed = True

    model_derivs = gpflow.gpr.GPR(x_full, f_full, kern=deriv_kernel)
    model_derivs.likelihood.variance = 1e-3
    model_derivs.likelihood.variance.fixed = True


    non_deriv_location = np.squeeze(x_full[:, 1] == 0)
    model_derivs2 = gpflow.gpr.GPR(x_full[non_deriv_location, :], f_full[non_deriv_location, :], kern=deriv_kernel2)
    model_derivs2.likelihood.variance = 1e-3
    model_derivs2.likelihood.variance.fixed = True


    model_deriv_rbf = gpflow.gpr.GPR(x_full, f_full, kern=deriv_kernel3)
    model_deriv_rbf.likelihood.variance = 1e-3
    model_deriv_rbf.likelihood.variance.fixed = True



    #print(x_full)
    #print(f_full)
    # No derivative kernel
    steps = []
    def callback(_):
        steps.append(time.time())
        print("step")

    model_no_derivs.optimize(maxiter=10, callback=callback)
    print(model_no_derivs)
    print(np.diff(steps))
    print(model_no_derivs.compute_log_likelihood())
    plot(model_no_derivs, x_axis, x_data, f_data)

    plt.show()
    #
    # # model predefined derivs
    # print(model_predefined_derivs)
    # print(model_predefined_derivs.compute_log_likelihood())
    # #plot(model_predefined_derivs, x_axis, x_data, f_data)  # this will not work
    # #plt.show()

    print("Model deriv rbf")
    model_deriv_rbf.optimize(maxiter=10, callback=callback)
    print(model_deriv_rbf)
    print(model_deriv_rbf.compute_log_likelihood())
    plot(model_deriv_rbf, np.concatenate((x_axis[:, :], np.zeros_like(x_axis)[:, :]), axis=1), x_data,
         f_data)
    plt.show()

    print("basic deriv model")
    # Model with derivative observations
    model_with_deriv = True
    if model_with_deriv:
        steps.clear()
        model_derivs.optimize(maxiter=10, callback=callback)
        print(model_derivs)
        print(model_derivs.compute_log_likelihood())
        plot(model_derivs, np.concatenate((x_axis[:, :], np.zeros_like(x_axis)[:, :]), axis=1), x_data, f_data)
        plt.show()


    # Model with derivative observations but does not use them
    model_no_derivbative_use = False
    if model_no_derivbative_use:
        print(model_derivs2)
        print(model_derivs2.compute_log_likelihood())
        plot(model_derivs2, np.concatenate((x_axis[:, :], np.zeros_like(x_axis)[:, :]), axis=1), x_data, f_data)
        plt.show()






if __name__ == '__main__':
    main()

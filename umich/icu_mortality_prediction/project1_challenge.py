# EECS 445 - Fall 2024
# Project 1 - project1.py

import numpy as np
import numpy.typing as npt
import pandas as pd
import yaml

# from helper import *
from helper_challenge import *
from matplotlib import pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn import metrics
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import resample
from sklearn.metrics import accuracy_score, precision_score, f1_score, roc_auc_score, average_precision_score, recall_score, confusion_matrix

config_challenge = yaml.load(open("config_challenge.yaml"), Loader=yaml.SafeLoader)
seed = config_challenge["seed"]
np.random.seed(seed)


from typing import Union, Dict


# Q1a
# Changed max to median + max
# Deselected ICUType
def generate_feature_vector(df: pd.DataFrame) -> dict[str, float]:
    """
    Reads a dataframe containing all measurements for a single patient
    within the first 48 hours of the ICU admission, and convert it into
    a feature vector.

    Args:
        df: dataframe with columns [Time, Variable, Value]

    Returns:
        a dictionary of format {feature_name: feature_value}
        for example, {'Age': 32, 'Gender': 0, 'max_HR': 84, ...}
    """
    # static_variables = config_challenge["static"]
    # timeseries_variables = config_challenge["timeseries"]
    # df = df

    # static, timeseries = df.iloc[0:5], df.iloc[5:]
    # static.loc[df['Value'] == -1, 'Value'] = np.nan

    # # # feature dictionary to return
    # feature_dict = {}

    # for static_variable in static_variables:
    #     # Check if the static_variable is present in the patient's data
    #     feature_row = static[static['Variable'] == static_variable]        
    #     if not feature_row.empty:
    #         # Get the value for the current variable
    #         feature_value = feature_row['Value'].values[0]            
    #         # Assign the value to the feature_dict for the corresponding variable
    #         feature_dict[static_variable] = feature_value
    #     else:
    #         # If the variable is missing, assign a default value (e.g., NaN or -1)
    #         feature_dict[static_variable] = np.nan
            
    # # timeseries variables to input in feature dictionary
    # for timeseries_variable in timeseries_variables:
    #     filtered_df = timeseries[timeseries['Variable'] == timeseries_variable]
    #     max_value = filtered_df['Value'].median() + filtered_df['Value'].max()
    #     feature_dict['max_' + timeseries_variable] = max_value

    # return feature_dict

    static_variables = config_challenge["static"]
    timeseries_variables = config_challenge["timeseries"]

    # Split static and time-series data
    static, timeseries = df.iloc[0:5], df.iloc[5:].copy()  # Explicitly make a copy of timeseries part
    static.loc[static['Value'] == -1, 'Value'] = np.nan

    # Feature dictionary to return
    feature_dict = {}


    for static_variable in static_variables:
        feature_row = static[static['Variable'] == static_variable]
        feature_value = feature_row['Value'].values[0] if not feature_row.empty else np.nan
        feature_dict[static_variable] = feature_value

    timeseries['Time'] = timeseries['Time'].apply(lambda x: f"{x}:00" if len(x) == 5 else x)


    timeseries['Time_hours'] = pd.to_timedelta(timeseries['Time']).dt.total_seconds() / 3600


    for timeseries_variable in timeseries_variables:
        filtered_df = timeseries[timeseries['Variable'] == timeseries_variable]
        first_24h = filtered_df[filtered_df['Time_hours'] <= 24]
        last_24h = filtered_df[filtered_df['Time_hours'] > 24]

        first_24h_mean = first_24h['Value'].mean() if not first_24h.empty else 0
        last_24h_mean = last_24h['Value'].mean() if not last_24h.empty else 0
        
 
        weighted_mean = (first_24h_mean + 3 * last_24h_mean) / 3
        
 
        first_24h_max = first_24h['Value'].max() if not first_24h.empty else np.nan
        last_24h_max = last_24h['Value'].max() if not last_24h.empty else np.nan
        weighted_max = (first_24h_max + 2 * last_24h_max) / 3
        feature_dict['weighted_mean_' + timeseries_variable] = weighted_mean
        feature_dict['weighted_max_' + timeseries_variable] = weighted_max

    return feature_dict





# Q1b - Done!
def impute_missing_values(X: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    For each feature column, impute missing values  (np.nan) with the
    population mean for that feature.

    Args:
        X: (N, d) matrix. X could contain missing values
    
    Returns:
        X: (N, d) matrix. X does not contain any missing values
    """
    for j in range(X.shape[1]):
        mean_value = np.nanmean(X[:, j])     
        X[:, j] = np.where(np.isnan(X[:, j]), mean_value, X[:, j])

    return X


# Q1c - Done!
def normalize_feature_matrix(X: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    For each feature column, normalize all values to range [0, 1].

    Args:
        X: (N, d) matrix.
    
    Returns:
        X: (N, d) matrix. Values are normalized per column.
    """
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    return X


# Helper function for performance - Done!
def calculate_metrics(
    clf_trained: Union[KernelRidge, LogisticRegression],
    X: npt.NDArray[np.float64],
    y_true: npt.NDArray[np.int64],
    y_pred: npt.NDArray[np.int64],
    metric: str = "accuracy"
) -> np.float64:

    # TODO: to add for 2d  
    # y_pred = clf_trained.predict(X)

    # y_pred = np.where(y_pred >= 0, 1, 0)
    # # y_true = np.where(y_true >= 0, 1, 0)

    score = 0
    
    if isinstance(clf_trained, KernelRidge):
        y_pred = np.where(y_pred >= 0, 1, 0)
        y_true = np.where(y_true >= 0, 1, 0)

    
    if metric == "accuracy":
        score = accuracy_score(y_true, y_pred)    
    elif metric == "precision":
        score = precision_score(y_true, y_pred, average = 'binary', labels=[-1, 1])   
    elif metric == "f1_score":
        score = f1_score(y_true, y_pred, average = 'binary', labels=[-1, 1])   
    elif metric == "auroc":
        # Handle LogisticRegression and KernelRidge separately
        if isinstance(clf_trained, LogisticRegression):
            score = roc_auc_score(y_true, clf_trained.decision_function(X), labels=[-1, 1])
        else:
            # KernelRidge predicts continuous outputs, use it for ROC
            # TODO: to 
            score = roc_auc_score(y_true, clf_trained.predict(X), labels=[-1, 1])   
    elif metric == "average_precision":
        
        if isinstance(clf_trained, LogisticRegression):
            score = average_precision_score(y_true, clf_trained.decision_function(X))           
        else:
            score = average_precision_score(y_true, clf_trained.predict(X))
    elif metric == "sensitivity":
        # Sensitivity is the same as recall
        score = recall_score(y_true, y_pred, average = 'binary', labels=[-1, 1])   
    elif metric == "specificity":
        # Specificity is calculated from confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[-1, 1]).ravel()
        score = tn / (tn + fp)
        score = 0
    return score


# Performance function - Done!
def performance(
    clf_trained: Union[KernelRidge, LogisticRegression],
    X: npt.NDArray[np.float64],
    y_true: npt.NDArray[np.int64],
    metric: str = "accuracy",
    bootstrap: bool = True
) -> Union[tuple[np.float64, np.float64, np.float64], np.float64]:
    """
    Calculates the performance metric as evaluated on the true labels
    y_true versus the predicted scores from clf_trained and X, using 1,000 
    bootstrapped samples of the test set if bootstrap is set to True. Otherwise,
    returns single sample performance as specified by the user. Note: you may
    want to implement an additional helper function to reduce code redundancy.
    
    Args:
        clf_trained: a fitted instance of sklearn estimator
        X : (n,d) np.array containing features
        y_true: (n,) np.array containing true labels
        metric: string specifying the performance metric (default='accuracy'
                other options: 'precision', 'f1-score', 'auroc', 'average_precision', 
                'sensitivity', and 'specificity')
    Returns:
        if bootstrap is True: the median performance and the empirical 95% confidence interval in np.float64
        if bootstrap is False: peformance 
    """

    bootstrapped_scores = []
    score = 0

    if (bootstrap == False):
        y_pred = clf_trained.predict(X)
        # y_pred = np.where(y_pred >= 0, 1, 0)
        score = calculate_metrics(clf_trained, X, y_true, y_pred, metric)
        return score
    else:
        for i in range(1000):
            # Bootstrap sample with replacement
            # indices = np.random.choice(len(y_true), size=len(y_true), replace=True)
            # X_boot = X[indices]
            # y_boot = y_true[indices]
            X_boot, y_boot = resample(X, y_true, replace=True, random_state=None)

            # Predict and calculate metrics for the bootstrap sample
            y_pred_boot = clf_trained.predict(X_boot)

            score = calculate_metrics(clf_trained, X_boot, y_boot, y_pred_boot, metric)
            bootstrapped_scores.append(score)

        bootstrapped_scores = np.array(bootstrapped_scores)
        median_score = np.nanmedian(bootstrapped_scores)
        lower_bound = np.percentile(bootstrapped_scores, 2.5)
        upper_bound = np.percentile(bootstrapped_scores, 97.5)
        return median_score, lower_bound, upper_bound
    return None


# Q2.1a - Done!
def cv_performance(
    clf: Union[KernelRidge, LogisticRegression],
    X: npt.NDArray[np.float64],
    y: npt.NDArray[np.int64],
    metric: str = "accuracy",
    k: int = 5,
) -> tuple[float, float, float]:
    """
    Splits the data X and the labels y into k-folds and runs k-fold
    cross-validation: for each fold i in 1...k, trains a classifier on
    all the data except the ith fold, and tests on the ith fold.
    Calculates the k-fold cross-validation performance metric for classifier
    clf by averaging the performance across folds.
    
    Args:
        clf: an instance of a sklearn classifier
        X: (n,d) array of feature vectors, where n is the number of examples
           and d is the number of features
        y: (n,) vector of binary labels {1,-1}
        k: the number of folds (default=5)
        metric: the performance metric (default='accuracy'
             other options: 'precision', 'f1-score', 'auroc', 'average_precision',
             'sensitivity', and 'specificity')
    
    Returns:
        a tuple containing (mean, min, max) 'cross-validation' performance across the k folds
    """
    # StratifiedKFold() to subdivide
    skf = StratifiedKFold(n_splits = k)
    performance_scores = []

    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        clf.fit(X_train, y_train)
        score = performance(clf, X_test, y_test, metric, bootstrap=False) # no bootstrapping
        performance_scores.append(score)
    
    mean_score = np.mean(performance_scores)
    min_score = np.min(performance_scores)
    max_score = np.max(performance_scores)
    
    return mean_score, min_score, max_score
    

# Q2.1b - Done!
def select_param_logreg(
    X: npt.NDArray[np.float64],
    y: npt.NDArray[np.int64],
    metric: str = "accuracy",
    k: int = 5,
    C_range: list[float] = [],
    penalties: list[str] = ["l1", "l2"],
) -> tuple[float, str]:
    """
    Sweeps different settings for the hyperparameter of a logistic regression,
    calculating the k-fold CV performance for each setting on X, y.
    
    Args:
        X: (n,d) array of feature vectors, where n is the number of examples
        and d is the number of features
        y: (n,) array of binary labels {1,-1}
        k: the number of folds (default=5)
        metric: the performance metric for which to optimize (default='accuracy',
             other options: 'precision', 'f1-score', 'auroc', 'average_precision', 'sensitivity',
             and 'specificity')
        C_range: an array with C values to be searched over
        penalties: a list of strings specifying the type of regularization penalties to be searched over
    
    Returns:
        The hyperparameters for a logistic regression model that maximizes the
        average k-fold CV performance.
    """
    # TODO: Implement this function
    # NOTE: You should be using your cv_performance function here
    # to evaluate the performance of each logistic regression classifier

    best_score = -np.inf  # Initialize to a low score (assuming higher is better for the metric)
    best_C = None
    best_penalty = None

    # Loop over each combination of C and penalty
    for penalty in penalties:
        for C in C_range:
            try:
                # Create a logistic regression model with the current C and penalty
                model = LogisticRegression(
                    penalty=penalty, 
                    C=C, 
                    solver='liblinear', 
                    fit_intercept=False, 
                    random_state=seed
                )

                mean_score, min_score, max_score = cv_performance(model, X, y, metric=metric, k=k)

                if mean_score > best_score:
                    best_score = mean_score
                    best_C = C
                    best_penalty = penalty

            except ValueError as e:
                print(f"Error with C={C}, penalty={penalty}: {e}")
                continue

    return best_C, best_penalty


# Q4c
def select_param_RBF(
    X: npt.NDArray[np.float64],
    y: npt.NDArray[np.int64],
    metric: str = "accuracy",
    k: int = 5,
    C_range: list[float] = [],
    gamma_range: list[float] = [],
) -> tuple[float, float]:
    """
    Sweeps different settings for the hyperparameter of a RBF Kernel Ridge Regression,
    calculating the k-fold CV performance for each setting on X, y.
    
    Args:
        X: (n,d) array of feature vectors, where n is the number of examples
        and d is the number of features
        y: (n,) array of binary labels {1,-1}
        k: the number of folds (default=5)
        metric: the performance metric (default='accuracy',
             other options: 'precision', 'f1-score', 'auroc', 'average_precision',
             'sensitivity', and 'specificity')
        C_range: an array with C values to be searched over
        gamma_range: an array with gamma values to be searched over
    
    Returns:
        The parameter value for a RBF Kernel Ridge Regression that maximizes the
        average k-fold CV performance.
    """
    # print(f"RBF Kernel Ridge Regression Model Hyperparameter Selection based on {metric}:")
    # TODO: Implement this function acording to the docstring
    # NOTE: This function should be very similar in structure to your implementation of select_param_logreg()
    best_score = -np.inf  # Initialize to a low score (assuming higher is better for the metric)
    best_C = None
    best_gamma = None

    # Loop over each combination of C and penalty
    for gamma in gamma_range:
        for C in C_range:
            try:
                # Create a logistic regression model with the current C and penalty
                model = KernelRidge(alpha=1/(2*C), kernel='rbf', gamma=gamma)
                # print("hi")
                # Get the mean cross-validation performance using cv_performance
                mean_score, min_score, max_score = cv_performance(model, X, y, metric=metric, k=k)

                # Update the best score, C, and penalty if the current score is better
                # print("Metric: ", metric, " Penalty: ", penalty, ", C: ", C, ", Mean: ", mean_score, ", Min: ", min_score, ", Max: ", max_score)
                if mean_score > best_score:
                    best_score = mean_score
                    best_C = C
                    best_gamma = gamma

            except ValueError as e:
                # Handle potential issues with solvers not supporting certain penalties
                print(f"Error with C={C}, gamma={gamma}: {e}")
                continue

    # Return the best C and penalty
    return best_C, best_gamma
    return None


# Q2.1e - Done!
def plot_weight(
    X: npt.NDArray[np.float64],
    y: npt.NDArray[np.int64],
    C_range: list[float],
    penalties: list[str],
) -> None:
    """
    The funcion takes training data X and labels y, plots the L0-norm
    (number of nonzero elements) of the coefficients learned by a classifier
    as a function of the C-values of the classifier, and saves the plot.
    Args:
        X: (n,d) array of feature vectors, where n is the number of examples
        and d is the number of features
        y: (n,) array of binary labels {1,-1}
    
    Returns:
        None
    """

    print("Plotting the number of nonzero entries of the parameter vector as a function of C")

    for penalty in penalties:
        # elements of norm0 should be the number of non-zero coefficients for a given setting of C
        norm0 = []
        for C in C_range:
            clf = LogisticRegression(penalty=penalty, C=C, solver='liblinear', fit_intercept=False, random_state=seed)
            clf.fit(X, y)

            w = clf.coef_.flatten()

            non_zero_count = np.count_nonzero(w)
            norm0.append(non_zero_count)

        # This code will plot your L0-norm as a function of C
        plt.plot(C_range, norm0)
        plt.xscale("log")
    plt.legend([penalties[0], penalties[1]])
    plt.xlabel("Value of C")
    plt.ylabel("Norm of theta")
    print(plt)
    # NOTE: plot will be saved in the current directory
    plt.savefig("L0_Norm.png", dpi=200)
    plt.close()


def main() -> None:

    ### Testing Prep ---------------------------
    print("Prep")
    metric_list = [
        # "accuracy",
        # "precision",
        "f1_score",
        "auroc",
        # "average_precision",
        # "sensitivity",
        # "specificity",
    ]
    C_range=[0.001, 0.01, 0.1, 0.5, 1, 1.5, 10, 100, 1000]
    print(f"Using Seed={seed}")
    X_train, y_train, X_test, feature_names = get_challenge_data()
    ### ----------------------------------------

    ### Construction of benchmark ----------------------
    ## Construct initial benchmark
    print("Testing:")
    def testing():
        # Add to maximize C
        C_table = {}
        # from sklearn.preprocessing import PolynomialFeatures

        # poly = PolynomialFeatures(degree=2, interaction_only=False)
        # X_train = poly.fit_transform(X_train)
        # from sklearn.preprocessing import PolynomialFeatures

        # poly = PolynomialFeatures(degree=2, interaction_only=False)
        # X_train = poly.fit_transform(X_train)
        performance_measures = metric_list
        C_value = []
        penalty = []
        cv_performances = []
        best_C_auroc, _ = select_param_logreg(X_train, y_train, "auroc", 5, [1, 1.2, 1.4, 1.6, 1.8])
        print(best_C_auroc)
        # best_C_auroc = 1
        benchmark_model = LogisticRegression(penalty='l1', C=best_C_auroc, solver='liblinear', fit_intercept=False, random_state=seed, class_weight = {-1:1, 1:6})
        benchmark_model.fit(X_train, y_train)
        cv_performances = []
        
        y_pred = benchmark_model.predict(X_test)
        y_score = benchmark_model.decision_function(X_test)

        generate_challenge_labels(y_pred, y_score, "author")

        
        cm = confusion_matrix(y_test, y_pred)

        
        print("Confusion Matrix:")
        print(cm)

        
        

        for metric in metric_list:
            mean_cv_perf, min_cv_perf, max_cv_perf = cv_performance(benchmark_model, X_train, y_train, metric, 5)
            cv_perf_value = f"{mean_cv_perf:.5f} ({min_cv_perf:.5f} {max_cv_perf:.5f})"
            cv_performances.append(cv_perf_value)
            print(metric)
        C_table = {
            'Performance Measures': metric_list,
            'Mean (Min, Max) CV Performance': cv_performances
        }
        C_table_df = pd.DataFrame(C_table)
        return C_table_df
    print(testing())
    return
    ### ------------------------------------------------

    ## Test benchmark
    # Benchmark mean
    
    def benchmark_mean_test():
        print("Benchark mean")
        C_table = {}
        performance_measures = metric_list
        C_value = []
        penalty = []
        cv_performances = []
        best_C_auroc, _ = (select_param_logreg(X_train, y_train, "auroc", 5, [2, 3, 4, 5, 6, 7, 8]))
        best_C_f1, _ = (select_param_logreg(X_train, y_train, "f1_score", 5, [1, 10, 100, 1000]))
        best_C_value = best_C_auroc
        best_penalty = 'l1'
        for metric in performance_measures:
            print(metric)
            # best_C_value, best_penalty = (select_param_logreg(X_train, y_train, metric, 5,[0.85, 0.9, 1, 1.1, 1.2, 100, 1000]))
            C_value.append(best_C_value)
            penalty.append(best_penalty)
            print(metric)
            best_model = LogisticRegression(penalty=best_penalty, C=best_C_value, solver='liblinear', fit_intercept=False, random_state=seed, class_weight = {-1:1, 1:10})
            model = best_model
            model.fit(X_train, y_train)
            mean_cv_perf, min_cv_perf, max_cv_perf = cv_performance(model, X_train, y_train, metric, 5)
            cv_perf_value = f"{mean_cv_perf:.5f} ({min_cv_perf:.5f} {max_cv_perf:.5f})"
            cv_performances.append(cv_perf_value)
            print(metric)
        C_table = {
            'Performance Measures': metric_list,
            'C': C_value,
            'Penalty': penalty,
            'Mean (Min, Max) CV Performance': cv_performances
        }
        C_table_df = pd.DataFrame(C_table)
        return C_table_df
    print(benchmark_mean_test())
    # return
    # Benchmark median
    def benchmark_median_test():
        print("Benchmark median")
        median_perf_list = []
        CI_list = []
        for metric in metric_list:
            best_C, best_penalty = select_param_logreg(X_train, y_train, metric=metric, C_range=[0.85, 0.9, 1, 1.1, 1.2, 100, 1000], penalties=["l1", "l2"])
            best_model = LogisticRegression(penalty=best_penalty, C=best_C, solver='liblinear', fit_intercept=False, random_state=seed, class_weight = {-1:1, 1:10})
            model = best_model
            model.fit(X_train, y_train)
            median_perf, lower_bound, upper_bound = performance(model, X_test, y_test, metric, bootstrap=True)
            median_perf_list.append(median_perf)
            CI_list.append(upper_bound - lower_bound)
        print("table")    
        table_bootstrapped = {
            "Performance Measures": metric_list,
            "Median Performance": median_perf_list,
            "(95% Confidence Interval)": CI_list
        }
        return pd.DataFrame(table_bootstrapped)
    # print(benchmark_median_test())
    # return
    ## Test 2.e - Done!
    def test_part_2e():
        print("2e")
        plot_weight(X_train, y_train, C_range, ['l2', 'l1'])
    # test_part_2e()
    # return
    ## Test 2.f - Done!
    def test_part_2f():
        print("2f")
        clf = LogisticRegression(penalty = 'l1', C = 1, solver='liblinear', fit_intercept=False, random_state=seed)
        clf.fit(X_train, y_train)
        theta = clf.coef_.flatten()
        largest_four = np.argsort(theta)[-4:]
        smallest_four = np.argsort(theta)[:4]
        smallest_features = [feature_names[i] for i in smallest_four]
        largest_features = [feature_names[i] for i in largest_four]
        table_smallest = {
            "Negative coefficient": theta[smallest_four],
            "Feature Name": smallest_features
        }
        table_largest = {
            "Positive coefficient": theta[largest_four],
            "Feature Name": largest_features
        }  
        return pd.DataFrame(table_smallest), pd.DataFrame(table_largest)
    # table_smallest_df, table_largest_df = test_part_2f()
    # print(table_smallest_df)
    # print(table_largest_df)
    # return
    ### ----------------------------------------

    ### Testing of Part 3 ----------------------
    # print("Part 3")
    ## Test 3.1b - Done!
    def test_part_3_1b():
        print("3.1b")
        median_perf_weight_list = []
        CI_perf_weight_list = []
        best_model = LogisticRegression(penalty='l2', C=1, solver='liblinear', fit_intercept=False, random_state=seed, class_weight = {-1:1, 1:50})
        best_model.fit(X_train, y_train)
        for metric in metric_list:
            median_perf, lower_bound, upper_bound = performance(best_model, X_test, y_test, metric, bootstrap=True)
            median_perf_weight_list.append(median_perf)
            CI_perf_weight_list.append(upper_bound - lower_bound)
        table_bootstrapped_weight = {
            "Performance Measures": metric_list,
            "Median Performance": median_perf_weight_list,
            "(95% Confidence Interval)": CI_perf_weight_list
        }
        return pd.DataFrame(table_bootstrapped_weight)
    # print(test_part_3_1b())
    # return
    ## Test 3.2a-b - Done!
    def test_part_3_2ab():
        print("3.2ab")
        # Find ideal Wn and Wp
        median_perf_best = -np.inf
        best_weight = 1
        i = 1
        y_true_pos = np.sum(y_train == 1)
        y_true_neg = np.sum(y_train == -1)
        best_weight = int(y_true_neg/y_true_pos)
        median_perf_weight_list = []
        CI_perf_weight_list = []         
        for metric in metric_list:
            best_model = LogisticRegression(penalty='l2', C=1, solver='liblinear', fit_intercept=False, random_state=seed, class_weight = {-1:1, 1:best_weight})
            best_model.fit(X_train, y_train)
            median_perf, lower_bound, upper_bound = performance(best_model, X_test, y_test, metric, bootstrap=True)
            median_perf_weight_list.append(median_perf)
            CI_perf_weight_list.append(upper_bound - lower_bound)
            table_bootstrapped_weight = {
                "Performance Measures": metric_list,
                "Median Performance": median_perf_weight_list,
                "(95% Confidence Interval)": CI_perf_weight_list
            }
        return pd.DataFrame(table_bootstrapped_weight)
    # print(test_part_3_2ab())
    # return
    ### ----------------------------------------

    # Read challenge data
    # TODO: Question 5: Apply a classifier to heldout features, and then use
    #       generate_challenge_labels to print the predicted labels
    # X_challenge, y_challenge, X_heldout, feature_names = get_challenge_data()


if __name__ == "__main__":
    main()


# Questions:
# RobustScaler from sklearn.preprocessing or KNNImputer from sklearn.impute.

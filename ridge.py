import itertools
import numpy as np

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

import specials, njva, approval, washington
from all import *

START_YEAR = 1994
LAST_YEAR = 2022
PREDICTION_YEAR = 2026

ALPHAS = np.logspace(-3, 3, 49)

MIDTERM_PV = {
    2022: -2.7,
    2018: 8.6,
    2014: -5.7,
    2010: -6.8,
    2006: 8.0,
    2002: -4.8,
    1998: -1.1,
    1994: -6.8,
}


def margin_to_str(margin: float):
    party = "D" if margin >= 0 else "R"
    return f"{party}+{abs(margin):.2f}"


special = specials.specials()
nj_gov, va_gov = njva.nj_va()
wa_primary = washington.wa_primary()
approval_values = approval.approval()

PREDICTORS = {
    "S": special,
    "NJ": nj_gov,
    "VA": va_gov,
    "WA": wa_primary,
    "A": approval_values,
}

predictor_names = list(PREDICTORS)

years = [
    year for year in sorted(MIDTERM_PV)
    if START_YEAR <= year <= LAST_YEAR
    and all(year in values for values in PREDICTORS.values())
]

y = np.array([MIDTERM_PV[year] for year in years], dtype=float)

X_all = np.array([
    [PREDICTORS[name][year] for name in predictor_names]
    for year in years
], dtype=float)

x_2026_all = np.array([
    [PREDICTORS[name][PREDICTION_YEAR] for name in predictor_names]
], dtype=float)


def fit_ridge(X_train, y_train, alpha):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    model = Ridge(alpha=alpha)
    model.fit(X_scaled, y_train)

    return scaler, model


def predict_ridge(scaler, model, X_test):
    return model.predict(scaler.transform(X_test))


def loo_predictions(X, y, alpha):
    predictions = np.empty(len(y))

    for i in range(len(y)):
        mask = np.arange(len(y)) != i
        scaler, model = fit_ridge(X[mask], y[mask], alpha)
        predictions[i] = predict_ridge(
            scaler, model, X[i:i + 1]
        )[0]

    return predictions


def select_alpha(X, y):
    best_alpha = None
    best_rmse = float("inf")

    for alpha in ALPHAS:
        predictions = loo_predictions(X, y, alpha)
        rmse = np.sqrt(np.mean((predictions - y) ** 2))

        if rmse < best_rmse:
            best_rmse = rmse
            best_alpha = alpha

    return best_alpha


def evaluate_subset(indices):
    X = X_all[:, indices]
    predictions = np.empty(len(y))

    # Outer LOOCV: tune alpha using only the training observations.
    for i in range(len(y)):
        mask = np.arange(len(y)) != i
        X_train, y_train = X[mask], y[mask]

        alpha = select_alpha(X_train, y_train)
        scaler, model = fit_ridge(X_train, y_train, alpha)
        predictions[i] = predict_ridge(
            scaler, model, X[i:i + 1]
        )[0]

    errors = predictions - y

    # Fit the final model using all historical observations.
    final_alpha = select_alpha(X, y)
    scaler, model = fit_ridge(X, y, final_alpha)

    prediction_2026 = predict_ridge(
        scaler, model, x_2026_all[:, indices]
    )[0]

    return {
        "names": [predictor_names[i] for i in indices],
        "predictions": predictions,
        "errors": errors,
        "rmse": np.sqrt(np.mean(errors ** 2)),
        "mae": np.mean(np.abs(errors)),
        "final_alpha": final_alpha,
        "prediction_2026": prediction_2026,
        "coefficients": model.coef_,
        "intercept": model.intercept_,
    }

results = []

for size in range(1, len(predictor_names) + 1):
    for indices in itertools.combinations(range(len(predictor_names)), size):
        results.append(evaluate_subset(list(indices)))

results.sort(key=lambda r: r["rmse"])

print("\nAll subsets, ranked by nested LOOCV RMSE:")
for rank, result in enumerate(results, start=1):
    print(f"\n{rank}. {' + '.join(result['names'])}")
    print(f"   RMSE: {result['rmse']:.3f}")
    print(f"   MAE:  {result['mae']:.3f}")
    print(f"   Final alpha: {result['final_alpha']:.6g}")
    print(
        f"   2026 prediction: "
        f"{margin_to_str(result['prediction_2026'])} "
        f"({result['prediction_2026']:+.2f})"
    )

    print("   Historical LOOCV predictions:")
    for year, actual, predicted in zip(
        years, y, result["predictions"]
    ):
        print(
            f"      {year}: actual {margin_to_str(actual):>7}, "
            f"predicted {margin_to_str(predicted):>7}, "
            f"error {predicted-actual:+.2f}"
        )

    print("   Coeffs:", result["coefficients"])
    print("   Intercept:", result["intercept"])

for result in results:
    names = "+".join(result["names"])
    print(f"{names}: {margin_to_str(result['prediction_2026'])}, RMSE {result['rmse']:.3f}, MAE {result['mae']:.3f}")

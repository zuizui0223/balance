// BALANCE plant confirmatory model v3
// Frozen before confirmatory architecture outcomes were independently coded.
data {
  int<lower=1> N;
  int<lower=2> K;
  int<lower=1> P;
  matrix[N, P] X;
  array[N] int<lower=1, upper=K> y;
  real<lower=0> slope_prior_sd;
  real<lower=0> intercept_prior_sd;
}
parameters {
  // Column k represents logit(response k+1 versus reference response 1 = SHARED).
  matrix[P, K - 1] beta;
}
model {
  for (k in 1:(K - 1)) {
    beta[1, k] ~ normal(0, intercept_prior_sd);
    for (p in 2:P) {
      beta[p, k] ~ normal(0, slope_prior_sd);
    }
  }

  for (n in 1:N) {
    vector[K] eta;
    eta[1] = 0;
    for (k in 2:K) {
      eta[k] = X[n] * beta[, k - 1];
    }
    y[n] ~ categorical_logit(eta);
  }
}
generated quantities {
  array[N] real log_lik;
  matrix[N, K] category_probability;

  for (n in 1:N) {
    vector[K] eta;
    vector[K] prob;
    eta[1] = 0;
    for (k in 2:K) {
      eta[k] = X[n] * beta[, k - 1];
    }
    prob = softmax(eta);
    log_lik[n] = categorical_logit_lpmf(y[n] | eta);
    for (k in 1:K) {
      category_probability[n, k] = prob[k];
    }
  }
}

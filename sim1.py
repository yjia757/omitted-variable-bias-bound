import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
# Set seed for reproducibility
np.random.seed(43)

## Data Generating
# Number of observations
n = 200000

# Generate baseline variables
L_0 = np.random.normal(0, 1, n)  # L_0 ~ Normal(0, 1)
U_0 = np.random.normal(0, 1, n)  # U_0 ~ Normal(0, 1)

# Generate A_0 (treatment at time t=0) based on L_0 and U_0
p_A0 = 1 / (1 + np.exp(-(0.5 * L_0 + 0.3 * U_0)))  # Logistic function
A_0 = np.random.binomial(1, p_A0, n)

# Generate L_1 (covariate at time t=1) based on L_0, A_0, and U_0
L_1 = 0.6 * L_0 + 0.4 * A_0 + 0.3 * U_0 + np.random.normal(0, 1, n)
# L_1 = 0.6 * L_0 + 0.3 * U_0 + np.random.normal(0, 1, n)  # A_0 does not cause L_1

# Generate A_1 (treatment at time t=1) based on L_1, A_0, and U_0
p_A1 = 1 / (1 + np.exp(-(0.4 * L_1 + 0.2 * A_0 + 0.3 * U_0)))  # Logistic function
A_1 = np.random.binomial(1, p_A1, n)

# Generate outcome Y based on L_0, L_1, A_0, A_1, and U_0
Y = 1.2 * L_0 + 0.8 * L_1 + 0.5 * A_0 + 0.7 * A_1 + 0.3 * U_0 + np.random.normal(0, 1, n)

# Create a DataFrame to store the generated data
data = pd.DataFrame({
    'L_0': L_0,
    'U_0': U_0,
    'A_0': A_0,
    'L_1': L_1,
    'A_1': A_1,
    'Y': Y
})
data['A_0A_1'] = np.where((data['A_0'] == 1) & (data['A_1'] == 1), 1, 0)

# Split the data into training and prediction sets
train_data = data[:100000]   # First 1000 rows for training
predict_data = data[100000:] # Last 1000 rows for prediction

## Building the OVB in lemma 1
# Step 1: estimate b1_true and attach to predict_data
train_subset_a0a1 = train_data[(train_data['A_0'] == 1) & (train_data['A_1'] == 1)]
X_train1 = train_subset_a0a1[['L_0', 'L_1', 'U_0']]
Y_train1 = train_subset_a0a1['Y']
model1 = LinearRegression()
model1.fit(X_train1, Y_train1)
X_predict1 = predict_data[['L_0', 'L_1', 'U_0']]
predict_data = predict_data.copy()  # Create an explicit copy to avoid SettingWithCopyWarning
predict_data.loc[:, 'b1_true'] = model1.predict(X_predict1)  # Use .loc for explicit assignment

# Step 2: estimate b1_short and attach to predict_data
X_train2 = train_subset_a0a1[['L_0', 'L_1']]
Y_train2 = train_subset_a0a1['Y']
model2 = LinearRegression()
model2.fit(X_train2, Y_train2)
X_predict2 = predict_data[['L_0', 'L_1']]
# No additional .copy() needed here as we already created one in Step 1
predict_data.loc[:, 'b1_short'] = model2.predict(X_predict2)  # Use .loc for consistency

# Step 5: estimate pi1_true
train_subset_a0 = train_data[train_data['A_0'] == 1]
X_train5 = train_subset_a0[['L_0', 'L_1', 'U_0']]
Y_train5 = train_subset_a0['A_1']
model5 = LogisticRegression()
model5.fit(X_train5, Y_train5)
X_predict5 = predict_data[['L_0', 'L_1', 'U_0']]
predict_data.loc[:, 'pi1_true'] = model5.predict_proba(X_predict5)[:, 1]

# Step 6: estimate pi1_short
X_train6 = train_subset_a0[['L_0', 'L_1']]
Y_train6 = train_subset_a0['A_1']
model6 = LogisticRegression()
model6.fit(X_train6, Y_train6)
X_predict6 = predict_data[['L_0', 'L_1']]
predict_data.loc[:, 'pi1_short'] = model6.predict_proba(X_predict6)[:, 1]

# Step 7: estimate pi0_true
X_train7 = train_data[['L_0', 'U_0']]
Y_train7 = train_data['A_0']
model7 = LogisticRegression()
model7.fit(X_train7, Y_train7)
X_predict7 = predict_data[['L_0', 'U_0']]
predict_data.loc[:, 'pi0_true'] = model7.predict_proba(X_predict7)[:, 1]

# Step 11: estimate pia1a0_true
X_train11 = train_data[['L_0', 'L_1', 'U_0']]
Y_train11 = train_data['A_0A_1']
model11 = LogisticRegression()
model11.fit(X_train11, Y_train11)
X_predict11 = predict_data[['L_0', 'L_1', 'U_0']]
predict_data.loc[:, 'pia1a0_true'] = model11.predict_proba(X_predict11)[:, 1]

# Step 8: estimate pi0_short
X_train8 = train_data[['L_0']]
Y_train8 = train_data['A_0']
model8 = LogisticRegression()
model8.fit(X_train8, Y_train8)
X_predict8 = predict_data[['L_0']]
predict_data.loc[:, 'pi0_short'] = model8.predict_proba(X_predict8)[:, 1]

# Step 12: estimate pia1a0_short
X_train12 = train_data[['L_0', 'L_1']]
Y_train12 = train_data['A_0A_1']
model12 = LogisticRegression()
model12.fit(X_train12, Y_train12)
X_predict12 = predict_data[['L_0', 'L_1']]
predict_data.loc[:, 'pia1a0_short'] = model12.predict_proba(X_predict12)[:, 1]

# Step 3: estimate b0_true
predict_train, predict_test = train_test_split(predict_data, test_size=0.5, random_state=42)
predict_train_subset = predict_train[predict_train['A_0'] == 1].copy()
X_train3 = predict_train_subset[['L_0', 'U_0']]
Y_train3 = predict_train_subset['b1_true']
model3 = LinearRegression()
model3.fit(X_train3, Y_train3)
X_test3 = predict_test[['L_0', 'U_0']]
# Copy predict_test to avoid SettingWithCopyWarning and attach b0_true
predict_test = predict_test.copy()  # Ensure it's a standalone DataFrame
predict_test.loc[:, 'b0_true'] = model3.predict(X_test3)  # Use .loc to clarify column assignment

# Step 10: estimate ite_b1b0_short_true
X_train10 = predict_train_subset[['L_0', 'U_0']]
Y_train10 = predict_train_subset['b1_short']
model10 = LinearRegression()
model10.fit(X_train10, Y_train10)
X_test10 = predict_test[['L_0', 'U_0']]
# Copy predict_test to avoid SettingWithCopyWarning and attach b0_true
predict_test.loc[:, 'ite_b1b0_short_true'] = model10.predict(X_test10)  # Use .loc to clarify column assignment

# Step 4: estimate b0_short
X_train4 = predict_train_subset[['L_0']]
Y_train4 = predict_train_subset['b1_short']
model4 = LinearRegression()
model4.fit(X_train4, Y_train4)
X_test4 = predict_test[['L_0']]
predict_test.loc[:, 'b0_short'] = model4.predict(X_test4)

# Step 9: calculating the bound
a0pi0_short = predict_test['A_0'] / predict_test['pi0_short']
a1pi1_short = predict_test['A_1'] / predict_test['pi1_short']
a1a0pia1a0_short = predict_test['A_0A_1'] / predict_test['pia1a0_short']
a0pi0_true = predict_test['A_0'] / predict_test['pi0_true']
a1pi1_true = predict_test['A_1'] / predict_test['pi1_true']
a1a0pia1a0_true = predict_test['A_0A_1'] / predict_test['pia1a0_true']

diff_b0 = predict_test['b0_short'] - predict_test['b0_true']
diff_b1 = predict_test['b1_short'] - predict_test['b1_true']

diff_a0pi0 = a0pi0_true - a0pi0_short
diff_a1pi1 = a1pi1_true - a1pi1_short

ovb_basic = np.mean(diff_b0 * diff_a0pi0 + a0pi0_short * diff_b1 * diff_a1pi1)

## Building the OVB in scratch paper
T1 = np.mean((predict_test['b0_short']- predict_test['ite_b1b0_short_true']) * diff_a0pi0)
T2 = np.mean((predict_test['ite_b1b0_short_true'] - predict_test['b0_true']) * diff_a0pi0)
T3 = np.mean(a0pi0_short * diff_b1 * diff_a1pi1)
ovb_dep = T1 + T2 + T3

## Calculate psi_short
psi_short = np.mean(predict_test['b0_short'] - a0pi0_short * predict_test['b0_short']
            - a0pi0_short * a1pi1_short * predict_test['b1_short']
            + a0pi0_short * predict_test['b1_short']
            + a0pi0_short * a1pi1_short * predict_test['Y'])
# Calculate psi_true
psi_true = np.mean(predict_test['b0_true'] - a0pi0_true * predict_test['b0_true']
            - a0pi0_true * a1pi1_true * predict_test['b1_true']
            + a0pi0_true * predict_test['b1_true']
            + a0pi0_true * a1pi1_true * predict_test['Y'])
# Calculate the difference between psi_short and psi_true
diff_psi = psi_short - psi_true

## Building the OVB in Theorem 2
B1 = T1
B2 = np.mean((predict_test['b1_short'] - predict_test['b1_true']) * (a1a0pia1a0_true - a1a0pia1a0_short))
ovb_adv = B1 + B2

## Debugging
K1 = T1
K2 = T2
K3 = np.mean(diff_b1 * (a1pi1_true * a0pi0_true - a1pi1_short * a0pi0_short))
K4 = np.mean(diff_b1 * (a0pi0_short - a0pi0_true))
ovb_debug = K1 + K2 + K3 + K4

# My proof on K2 + K4 = 0 is correct.
# The problematic part is my derivation on K3, in particular, the probability part.
# Let's check equation (21)
eq21 = np.mean(a1pi1_true * a0pi0_true - a1a0pia1a0_true)
# Let's check equation (22)
eq22 = np.mean(a1pi1_short * a0pi0_short - a1a0pia1a0_short)
# If A0 and L1 are independent, then ovb_adv is close.

# The mean is not zero
suppose = np.mean(a1pi1_true * a0pi0_true - a1pi1_short * a0pi0_short)
# The mean is zero
iwrote = np.mean(a1a0pia1a0_true - a1a0pia1a0_short)

## Collect the desired variables into a dictionary
results = {
    'Variable': ['diff_psi', 'ovb_basic', 'ovb_dep', 'ovb_debug', 'ovb_adv'],
    'Value': [diff_psi, ovb_basic, ovb_dep, ovb_debug, ovb_adv]
}
results_table = pd.DataFrame(results)
print(results_table)
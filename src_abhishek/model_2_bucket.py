import numpy as np
from tempfile import TemporaryFile
import pandas as pd
import sklearn.linear_model

features = 'potential,attacking_work_rate,defensive_work_rate,crossing,finishing,heading_accuracy,short_passing,volleys,dribbling,curve,free_kick_accuracy,long_passing,ball_control,acceleration,sprint_speed,agility,reactions,balance,shot_power,jumping,stamina,strength,long_shots,aggression,interceptions,positioning,vision,penalties,marking,standing_tackle,sliding_tackle,gk_diving,gk_handling,gk_kicking,gk_positioning,gk_reflexes'
features_list = features.split(',')
num_features = len(features_list)
features_list = features_list * 30

print(len(features_list))
k=0
for bucket_id in range(30):
    idx = bucket_id  * num_features
    for feature in features_list[ bucket_id  * num_features :  (bucket_id + 1 ) * num_features]:

        features_list[idx] = str(bucket_id) + "_" + features_list[idx]
        idx += 1

print features_list


def train_validate_test_split(df, train_percent=.8, validate_percent=0, seed=100):
    np.random.seed(seed)
    perm = np.random.permutation(df.index)
    m = len(df)
    train_end = int(train_percent * m)
    validate_end = int(validate_percent * m) + train_end
    train = df.ix[perm[:train_end]]
    validate = df.ix[perm[train_end:validate_end]]
    test = df.ix[perm[validate_end:]]
    return train, validate, test


outfile = 'alldata_buckets_4x3.npz'
npzfile = np.load(outfile)
print npzfile.files
all_data = npzfile['arr_0']
print(all_data.shape)

train_data, validate_data, test_data = train_validate_test_split(pd.DataFrame(all_data))

train_data = np.array(train_data)
validate_data = np.array(validate_data)
test_data = np.array(test_data)


train_X = train_data[:, :-1]

validate_X = validate_data[:, :-1]
test_X = test_data[:, :-1]
train_Y = train_data[:,-1]
validate_Y = validate_data[:,-1]
test_Y = test_data[:,-1]
print(train_X.shape)
print(validate_X.shape)
print(test_X.shape)

epsilon = 1e-12
mean_train = np.mean(train_X, axis = 0)
std_train = np.std(train_X, axis = 0) + epsilon
train_X = (train_X - mean_train)/std_train
test_X = (test_X - mean_train)/std_train

kbest = sklearn.linear_model.LogisticRegression(penalty='l1', C= 5)
kbest.fit(train_X, train_Y)
print('training accuracy', kbest.score(train_X, train_Y))
print('test accuracy', kbest.score(test_X, test_Y))
print('all coefficients', kbest.coef_)
best_features = np.argsort(np.abs(kbest.coef_))[::-1].reshape(1080*2)
#print('15 best features', best_features)
coefs = kbest.coef_
coefs = coefs.reshape(1080*2)
print(best_features.shape)
for idx, _ in  enumerate(coefs):
    print features_list[idx], ",", coefs[idx]

'''
import sklearn.ensemble

random_forest = sklearn.ensemble.RandomForestClassifier(n_estimators=10)
random_forest.fit_transform(train_X, train_Y)
print('training accuracy', random_forest.score(train_X, train_Y))
print('test accuracy', random_forest.score(test_X, test_Y))
print('random_forest features', random_forest.feature_importances_)

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
clf = DecisionTreeClassifier(random_state=0)
cross_val_score(clf, train_X, train_Y, cv=10)
print("Decision tree accuracy" , cross_val_score(clf, test_X, test_Y, cv=10))

from sklearn.decomposition import PCA

pca = PCA(n_components=25)
train_mean = np.mean(train_X, axis = 0)
train_std = np.std(train_X, axis=0)
train_X = (train_X - train_mean)/train_std
test_X = (test_X  - train_mean)/train_std

pca.fit_transform(train_X)

print(pca.explained_variance_ratio_)
#test_X = pca.transform(test_X)
kbest = sklearn.linear_model.LogisticRegression()
kbest.fit_transform(train_X, train_Y)
print('training accuracy after pca', kbest.score(train_X, train_Y))
print('test accuracy after ', kbest.score(test_X, test_Y))
print('all coefficients after pca', kbest.coef_)
best_features = np.argsort(np.abs(kbest.coef_))[::-1].reshape(144)
#print('15 best features', best_features)
print(best_features.shape)
for idx in  best_features:
    print features_list[idx]


from sklearn import svm
clf = svm.SVC()
clf.fit(train_X, train_Y)
preds = clf.predict(test_X)
mask = np.ones(test_Y.shape[0])
print(np.sum(mask[preds == test_Y]))

'''



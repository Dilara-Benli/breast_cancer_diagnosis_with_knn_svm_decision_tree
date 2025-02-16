import pandas as pd
import matplotlib.pyplot as plt
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, cohen_kappa_score
from sklearn.metrics import roc_curve, auc

class ModelTraining:
    def __init__(self, dataset_path):
        self.dataset = pd.read_excel(dataset_path)
        self.dataset = self.dataset.drop("ID", axis=1) # benim veri setime özel

        self.features = self.dataset.iloc[:, :-1].values 
        self.labels = self.dataset.iloc[:, -1].values     # son sütun = etiket, olarak kabul edilir

        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.features, self.labels, test_size=0.3, random_state=10)

        self.scaler = MinMaxScaler()
        self.x_train = self.scaler.fit_transform(self.x_train)
        self.x_test = self.scaler.transform(self.x_test)

    def find_best_k_value(self):
        test_scores = []
        for k in range(1, 21):
            knn = KNeighborsClassifier(n_neighbors=k)
            knn.fit(self.x_train, self.y_train)
            test_score = knn.score(self.x_test, self.y_test)
            test_scores.append(round(test_score, 4))

        max_test_score = max(test_scores)
        best_k_index = test_scores.index(max_test_score)
        best_k_value = best_k_index + 1

        return best_k_value

    def create_knn_model(self):
        best_k_value = self.find_best_k_value()
        knn_model = KNeighborsClassifier(n_neighbors=best_k_value)
        knn_model.fit(self.x_train, self.y_train)
        return knn_model

    def create_svm_model(self):
        svm_model = SVC(kernel="linear", probability=True)
        svm_model.fit(self.x_train, self.y_train)
        return svm_model

    def create_decision_tree_model(self):
        decision_tree_model = DecisionTreeClassifier(criterion="entropy")
        decision_tree_model.fit(self.x_train, self.y_train)
        return decision_tree_model
    
    def save_model(self, model, model_name):
        with open(f"{model_name}.pkl", "wb") as file:
            pickle.dump(model, file)
        print(f"{model_name} model saved successfully.")

    def load_model(self, model_name):
        with open(f"{model_name}.pkl", "rb") as file:
            model = pickle.load(file)
        return model

    def calculate_evaluation_metrics(self, model):
        predictions = model.predict(self.x_test)

        conf_matrix = confusion_matrix(self.y_test, predictions)
        
        accuracy = accuracy_score(self.y_test, predictions) # doğruluk
        precision = precision_score(self.y_test, predictions) # kesinlik
        recall = recall_score(self.y_test, predictions) # duyarlılık
        tn, fp, fn, tp = conf_matrix.ravel()
        specificity = tn / (tn + fp) # özgüllük
        f1 = f1_score(self.y_test, predictions)
        auc_score = roc_auc_score(self.y_test, predictions)
        kappa = cohen_kappa_score(self.y_test, predictions)

        print(f"Accuracy Score: {accuracy:.3f}\nPrecision Score: {precision:.3f}\nRecall Score: {recall:.3f}\nSpecificity Score: {specificity:.3f}\nF1 Score: {f1:.3f}\nAuc Score: {auc_score:.3f}\nKappa Score: {kappa:.3f}")

        return accuracy, precision, recall, specificity, f1, auc_score, kappa

    def plot_conf_matrix(self, model):
        predictions = model.predict(self.x_test)
        conf_matrix = confusion_matrix(self.y_test, predictions)
        conf_matrix_disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=model.classes_)
        conf_matrix_disp.plot()

    def plot_roc_curve(self, model):
        if hasattr(model, "predict_proba"): # knn, decision_tree
            proba_predictions = model.predict_proba(self.x_test)[:, 1]
        else:
            proba_predictions = model.decision_function(self.x_test)

        fpr, tpr, _ = roc_curve(self.y_test, proba_predictions)
        roc_auc = auc(fpr, tpr)
        plt.figure()
        plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        plt.show()



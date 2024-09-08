from flask import Flask, request, render_template
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-form', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('radio')
    bodyheight = request.form.get('bodyheight')
    bodyweight = request.form.get('bodyweight')
    gdp = request.form.get('gdp')
    gd2pp = request.form.get('gd2pp')

    try:
        bmi = check_bmi(bodyheight, bodyweight)
        bmi_message = f"BMI: {bmi:.2f}"
    except ValueError as e:
        bmi_message = str(e)

    try:
        predict = predict_diabet(float(bmi), float(gdp), float(gd2pp))
        if predict < 33:
            predict_message = 'Rendah'
        elif 33 <= predict <= 66:
            predict_message = 'Menengah'
        else:
            predict_message = 'Tinggi'
    except ValueError as e:
        predict_message = str(e)

    # Return the result page with the data
    return render_template('result.html', name=name, age=age, gender=gender, bodyheight=bodyheight, bodyweight=bodyweight, bmi_message=bmi_message, predict_message=predict_message)

def check_bmi(bodyheight, bodyweight):
    try:
        bodyheight = float(bodyheight)
        bodyweight = float(bodyweight)
    except ValueError:
        raise ValueError("Body height and body weight must be numeric.")
    
    bmi = bodyweight / (bodyheight / 100) ** 2
    return bmi

def predict_diabet(bmi, gdp, gd2pp):

    # Definisikan variabel input
    imt = ctrl.Antecedent(np.arange(10, 50, 1), 'IMT')  # IMT (kg/m^2)
    glukosa_gdp = ctrl.Antecedent(np.arange(50, 200, 1), 'Glukosa_GDP')  # GDP (mg/dL)
    glukosa_gd2pp = ctrl.Antecedent(np.arange(50, 300, 1), 'Glukosa_GD2PP')  # GD2PP (mg/dL)

    # Definisikan variabel output
    risiko = ctrl.Consequent(np.arange(0, 100, 1), 'Risiko_Diabetes')

    # Fungsi keanggotaan untuk IMT (BMI)
    imt['normal'] = fuzz.trimf(imt.universe, [18.5, 21, 23])
    imt['gemuk_ringan'] = fuzz.trimf(imt.universe, [23, 25, 27])
    imt['gemuk_berat'] = fuzz.trimf(imt.universe, [27, 30, 35])

    # Fungsi keanggotaan untuk Glukosa GDP
    glukosa_gdp['normal'] = fuzz.trimf(glukosa_gdp.universe, [70, 90, 100])
    glukosa_gdp['pre'] = fuzz.trimf(glukosa_gdp.universe, [100, 110, 125])
    glukosa_gdp['diabetes'] = fuzz.trimf(glukosa_gdp.universe, [125, 150, 200])

    # Fungsi keanggotaan untuk Glukosa GD2PP
    glukosa_gd2pp['normal'] = fuzz.trimf(glukosa_gd2pp.universe, [70, 120, 140])
    glukosa_gd2pp['pre'] = fuzz.trimf(glukosa_gd2pp.universe, [140, 160, 180])
    glukosa_gd2pp['diabetes'] = fuzz.trimf(glukosa_gd2pp.universe, [180, 220, 300])

    # Fungsi keanggotaan untuk Risiko Diabetes
    risiko['rendah'] = fuzz.trimf(risiko.universe, [0, 25, 50])
    risiko['sedang'] = fuzz.trimf(risiko.universe, [40, 50, 70])
    risiko['tinggi'] = fuzz.trimf(risiko.universe, [60, 75, 100])

    # Definisikan aturan fuzzy sesuai aturan yang diberikan
    rules = [
        ctrl.Rule(imt['normal'] & glukosa_gdp['normal'] & glukosa_gd2pp['normal'], risiko['rendah']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['normal'] & glukosa_gd2pp['pre'], risiko['sedang']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['normal'] & glukosa_gd2pp['diabetes'], risiko['sedang']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['pre'] & glukosa_gd2pp['pre'], risiko['tinggi']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['pre'] & glukosa_gd2pp['normal'], risiko['sedang']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['pre'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['pre'], risiko['tinggi']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['normal'], risiko['sedang']),
        ctrl.Rule(imt['normal'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['normal'] & glukosa_gd2pp['normal'], risiko['rendah']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['normal'] & glukosa_gd2pp['pre'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['normal'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['pre'] & glukosa_gd2pp['pre'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['pre'] & glukosa_gd2pp['normal'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['pre'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['pre'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['normal'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_ringan'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['normal'] & glukosa_gd2pp['normal'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['normal'] & glukosa_gd2pp['pre'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['normal'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['pre'] & glukosa_gd2pp['pre'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['pre'] & glukosa_gd2pp['normal'], risiko['sedang']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['pre'] & glukosa_gd2pp['diabetes'], risiko['tinggi']),
        ctrl.Rule(imt['gemuk_berat'] & glukosa_gdp['diabetes'] & glukosa_gd2pp['pre'], risiko['tinggi']),
    ]

    # Buat sistem kontrol fuzzy
    risiko_ctrl = ctrl.ControlSystem(rules)
    risiko_diabetes = ctrl.ControlSystemSimulation(risiko_ctrl)

    # Input data
    risiko_diabetes.input['IMT'] = bmi  # Contoh input IMT
    risiko_diabetes.input['Glukosa_GDP'] = gdp  # Contoh input Glukosa GDP
    risiko_diabetes.input['Glukosa_GD2PP'] = gd2pp  # Contoh input Glukosa GD2PP

    # Kalkulasi hasil
    risiko_diabetes.compute()

    # Output hasil risiko diabetes
    return risiko_diabetes.output['Risiko_Diabetes']

if __name__ == '__main__':
    app.run(debug=True)

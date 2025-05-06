from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .utils import TrainModel, Predict
from .models import TrainedModels
from django.urls import reverse
import pickle
import json


# Create your views here.
class HomeView(TemplateView):
    template_name = 'Home.html'


class TrainView(TemplateView):
    template_name = 'Train.html'
    model = TrainedModels

    def post(self, request, *args, **kwargs):
        print(request.FILES['trainingFile'])
        if request.FILES['trainingFile']:
            uploaded_file = request.FILES['trainingFile']
            name = request.POST.get('modelTitle')
            if uploaded_file.name.endswith('.csv'):
                # try:
                training = TrainModel()
                model, feature_columns, label_encoders, scaler, result = training.train_model(
                    uploaded_file, ['policy_number', 'policy_bind_date', 'insured_zip', 'policy_state',
                                    'incident_location', 'incident_date', 'incident_state', 'incident_city',
                                    'insured_hobbies', 'auto_make', 'auto_model', 'auto_year'])
                save_model = TrainedModels.objects.create(
                    name=name.title(),
                    model=pickle.dumps(model),
                    featured_columns=json.dumps(list(feature_columns)),
                    label_encoders=pickle.dumps(label_encoders),
                    scaler=pickle.dumps(scaler),
                    result=pickle.dumps(result)
                )
                save_model.save()
                return render(request, 'Response.html', {'message': 'Successfully Trained', 'type': 0})
                # except Exception as e:
                #     print(e)
                #     return JsonResponse({'message': 'Some error occurred. Contact Administrator!!'})
            else:
                return render(request, 'Response.html', {'message': 'Some Error Occurred', 'type': 1})


class PredictView(TemplateView):
    template_name = 'Predict.html'
    model = TrainedModels

    def post(self, request):
        db = self.model.objects.values().first()
        data = [request.POST.get(k) for k in json.loads(db['featured_columns'])]
        model = pickle.loads(db['model'])
        label_encoders = pickle.loads(db['label_encoders'])
        scaler = pickle.loads(db['scaler'])
        for i in range(len(data)):
            try:
                data[i] = float(data[i])
            except Exception:
                continue
        prediction = Predict(data, model, label_encoders, scaler)
        res = prediction.predict(eval(db['featured_columns']))
        if res:
            return render(request, 'Response.html', {'type': 1, 'message': 'Fraud !'})
        else:
            return render(request, 'Response.html', {'type': 0, 'message': 'Valid !'})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect(reverse('Home'))

    elif request.method == 'GET':
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('Home'))


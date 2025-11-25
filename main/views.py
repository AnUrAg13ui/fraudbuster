from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
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
        try:
            if 'trainingFile' not in request.FILES:
                return render(request, 'Response.html', {'message': 'Please upload a file', 'type': 1})
            
            uploaded_file = request.FILES['trainingFile']
            name = request.POST.get('modelTitle')
            
            if not name:
                return render(request, 'Response.html', {'message': 'Please provide a model title', 'type': 1})
            
            if not uploaded_file.name.endswith('.csv'):
                return render(request, 'Response.html', {'message': 'Please upload a CSV file', 'type': 1})
            
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
        
        except Exception as e:
            print(f'Training error: {str(e)}')
            return render(request, 'Response.html', {'message': f'Error during training: {str(e)}', 'type': 1})


class PredictView(TemplateView):
    template_name = 'Predict.html'
    model = TrainedModels

    def post(self, request):
        try:
            db = self.model.objects.values().first()
            
            if not db:
                return render(request, 'Response.html', {'message': 'No trained model found. Please train a model first.', 'type': 1})
            
            try:
                featured_columns = json.loads(db['featured_columns'])
                data = [request.POST.get(k) for k in featured_columns]
            except (json.JSONDecodeError, KeyError) as e:
                return render(request, 'Response.html', {'message': f'Error reading model data: {str(e)}', 'type': 1})
            
            try:
                model = pickle.loads(db['model'])
                label_encoders = pickle.loads(db['label_encoders'])
                scaler = pickle.loads(db['scaler'])
            except Exception as e:
                return render(request, 'Response.html', {'message': f'Error loading model: {str(e)}', 'type': 1})
            
            # Convert data to float
            for i in range(len(data)):
                try:
                    data[i] = float(data[i])
                except (ValueError, TypeError):
                    return render(request, 'Response.html', {'message': f'Invalid input for {featured_columns[i]}. Please enter numeric values.', 'type': 1})
            
            prediction = Predict(data, model, label_encoders, scaler)
            res = prediction.predict(featured_columns)
            
            if res:
                return render(request, 'Response.html', {'type': 1, 'message': 'Fraud !'})
            else:
                return render(request, 'Response.html', {'type': 0, 'message': 'Valid !'})
        
        except Exception as e:
            print(f'Prediction error: {str(e)}')
            return render(request, 'Response.html', {'message': f'Error during prediction: {str(e)}', 'type': 1})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('Home'))
        else:
            # authentication failed — show error on login page
            return render(request, 'login.html', {'error': 'Username or password is wrong'})

    elif request.method == 'GET':
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('Home'))


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # authenticate and log in
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
            return redirect(reverse('Home'))
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


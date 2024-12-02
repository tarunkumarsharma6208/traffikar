import asyncio
import httpx
import logging
from django.http import JsonResponse
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Asynchronous function to send requests
async def send_request(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            logger.info(f"Requested {url} - Status: {response.status_code}")
            return response.status_code
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return None


# Function to generate traffic
async def generate_traffic(url, request_count):
    tasks = []
    for _ in range(request_count):
        tasks.append(send_request(url))
        await asyncio.sleep(1)  # wait between requests
    results = await asyncio.gather(*tasks)
    return results


async def session_generate_traffic(url, request_count):
    tasks = [send_request(url) for _ in range(request_count)]
    return await asyncio.gather(*tasks)



# ======================================================================



def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  # Replace 'home' with your desired redirect URL name
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "account/login.html")

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')

        if username is None:
            messages.error(request, "Provide username!")
            return redirect('signup')

        if password1 is None or password1 is None:
            messages.error(request, "Password should not be none")
            return redirect('signup')
        
        if not password1 == password1:
            messages.error(request, "Password did't match!")
            return redirect('signup')
        
        user = UserProfile.objects.create_user(username=username,password=password1, first_name=fname, last_name=lname)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        
    return render(request, "account/signup.html")

def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, "loadtest/home.html") 

# Django view to handle load test form
@login_required(login_url='/login')
def load_test_view(request):
    if request.method == "POST":
        url = request.POST.get("url")
        login_url = request.POST.get("login_url")
        request_count = int(request.POST.get("request_count", 10))
        # time_interval = float(request.POST.get("time_interval", 1))

        # Save load test configuration
        load_test = LoadTest.objects.create(
            url=url, user=request.user, request_count=request_count, time_interval=1
        )

        # session = httpx.Client()

        # # Step 2: Log in and get session cookies
        # login_url = "http://192.168.1.14:8000/login/"
        # credentials = {"username": username, "password": password}
        
        # # Send login request
        # login_response = session.post(login_url, data=credentials)

        # # Check if login was successful (you can adjust this based on your login response)
        # if login_response.status_code == 200:
        #     print("Login successful!")
        # else:
        #     print("Login failed!")
        #     return JsonResponse({"error": "Login failed"}, status=400)

        # # Step 3: Perform the load test (send multiple requests)
        # successful_requests = 0
        # for i in range(request_count):
        #     response = session.get(url)
        #     print(f"Request {i + 1} - Status: {response.status_code}")
        #     if response.status_code == 200:
        #         successful_requests += 1

        # Run traffic generation in background
        results = asyncio.run(generate_traffic(url, request_count))
        for status_code in results:
            if status_code is not None:
                RequestLog.objects.create(test=load_test, url=url, status_code=status_code)

        return  redirect('load_test_results')

    return render(request, "loadtest/load_test.html")


@login_required(login_url='/login')
def advance_test_view(request):
    if request.method == "POST":
        url = request.POST.get("url")
        login_url = request.POST.get("login_url")
        username = request.POST.get("username")
        password = request.POST.get("password")
        request_count = int(request.POST.get("request_count", 10))

        # Save load test configuration
        load_test = LoadTest.objects.create(
            url=url, user=request.user, request_count=request_count, time_interval=1
        )

        try:
            # Run the traffic generation asynchronously
            async def run_test():
                # Perform login using httpx.AsyncClient
                async with httpx.AsyncClient(timeout=10) as session:
                    credentials = {"username": username, "password": password}
                    login_response = await session.post(login_url, data=credentials)

                    if login_response.status_code != 200:
                        logger.error("Login failed")
                        return JsonResponse({"error": "Login failed"}, status=400)

                    # Generate traffic using the send_request function
                    results = await session_generate_traffic(url, request_count)

                    # Log the results
                    for status_code in results:
                        if status_code is not None:
                            RequestLog.objects.create(
                                test=load_test, url=url, status_code=status_code
                            )

            # Run the async function
            asyncio.run(run_test())

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return JsonResponse({"error": "An internal error occurred"}, status=500)

        return redirect('advance_test_view')

    return render(request, "loadtest/advance_test.html")



@login_required(login_url='/login')
def load_test_results(request):
    load_test = LoadTest.objects.filter(user=request.user)

    
    lit = []
    for i in load_test:
        d = {}
        log1 = RequestLog.objects.filter(test=i)
        for j in log1:
            if j.status_code not in d:
                d['status_code'] = j.status_code
            if j.url not in d:
                d['url'] = j.url
        lit.append({
            'request_count': i.request_count,
            'data': d,
        })

    # You can enhance this with actual results if you store them
    return render(request, "loadtest/results.html", {"load_test": load_test, 'lit': lit})
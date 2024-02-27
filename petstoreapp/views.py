import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q 
from .models import Pet, Cart, CartItems
from .forms import PetForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'petstoreapp/home.html')

def pets_list(request):
    pets = Pet.objects.all()
    return render(request, 'petstoreapp/pets_list.html', {'pets': pets})
    #search_query = request.GET.get('search', '')
    #pets = Pet.objects.filter(name__icontains=search_query)
    #return render(request, 'petstoreapp/pets_list.html', {'pets': pets, 'search_query': search_query})

def pets_detail(request, pk):
    #pets = Pet.objects.get(pk=pk)
    pets = get_object_or_404(Pet, pk=pk)
    return render(request, 'petstoreapp/pets_detail.html', {'pets': pets})

def add_to_cart(request, pk):
    if request.method == 'POST':
        pet = get_object_or_404(Pet, pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the CartItem already exists for the pet in the cart
        cart_item, created = CartItems.objects.get_or_create(cart=cart, pet=pet, defaults={'quantity': quantity})

        # If the cart item already exists, update its quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # If the cart item is newly created, set its quantity
            cart_item.quantity = quantity
            cart_item.save()

        return redirect('cart')

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItems, id=cart_item_id)
    cart_item.delete()
    return redirect('cart') 
       
def cart_view(request):
    cart_items = CartItems.objects.filter(cart__user=request.user)
    return render(request, 'petstoreapp/cart.html', {'cart_items': cart_items})

def proceed_to_pay(request):
    cart_items = CartItems.objects.filter(cart__user=request.user)
    total_amount = sum(item.pet.price * item.quantity for item in cart_items)
    print("total amount in payment_confirmation --------> ", total_amount)
    return render(request, 'petstoreapp/proceed_to_pay.html', {'total_amount': total_amount})

@csrf_exempt
def payment_confirmation(request):
    # Your logic for payment confirmation here
    # Get the current user's cart
    cart = Cart.objects.get(user=request.user)
    
    # Get all cart items for the current user
    cart_items = CartItems.objects.filter(cart=cart)
    order_amount = 0

    # Calculate the total amount to be paid
    total_amount = sum(item.pet.price * item.quantity for item in cart_items)
    print("total amount in payment_confirmation --------> ", total_amount)
    # Initialize Razorpay client with your API key and secret
    client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
    
    # Create Razorpay order
    # order_amount = int(total_amount * 100)  # Razorpay expects amount in paise
    order_amount = (order_amount + total_amount) * 100
    print("order_amount in payment_confirmation ------------ > ", order_amount)
    order_currency = 'INR'  # Change currency as per your requirement
    order_receipt = 'order_rcptid_11'  # Replace with your order receipt ID
    order = client.order.create({'amount': order_amount, 'currency': order_currency, 'receipt': order_receipt})
    
    # Pass Razorpay order details to the payment_confirmation template
    context = {'order_amount': order_amount, 'order': order, 'razorpay_key_id': settings.RAZORPAY_TEST_KEY_ID}
    
    # Render the payment confirmation template
    
    return render(request, 'petstoreapp/payment_confirmation.html', context)

def pet_create(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)   
        if form.is_valid():
            form.save()
            return redirect('pets_list')
    else:
        form = PetForm()
    return render(request, 'petstoreapp/pet_create.html', {'form': form})

def search_results(request):
    search_query = request.GET.get('search', '')
    #pets = Pet.objects.filter(name__icontains=search_query)
    pets = Pet.objects.filter(Q(name__icontains=search_query) | Q(breed__icontains=search_query))
    return render(request, 'petstoreapp/search_results.html', {'pets': pets, 'search_query': search_query})

def my_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('pets_list')
        else:
            pass
    return render(request, 'petstoreapp/login.html')

def my_logout(request):
    logout(request)
    return redirect('home')

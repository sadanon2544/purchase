import stripe
from fastapi import FastAPI, Request, Header
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:4200/usagepackage",
    "https://0c98-180-183-133-248.ngrok-free.app"
]

app.add_middleware(SessionMiddleware,
                   secret_key="dVu9jfC1PPVGRkq-X5nKaP_vDHC63CxQ2K4W0QVpFJo",
                  )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# stripe.api_key = "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"
stripe.api_key ="sk_test_51NTdHJFm689lJVNLfCNn9s5TCRAuh7lCal7OX29k9VIgp5x3PZZhiSFHJXNImQWlNjxyLxl3yjG9h5LWQivNICA50008b276C9"

@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()

    user_id = data["google_id"]

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        # mode="subscription",
        mode='payment',
        line_items=[{
            "price": data["priceId"],
            "quantity": 1
        }],
        client_reference_id=user_id,
        success_url='http://localhost:4200/success',
        cancel_url='http://localhost:4200/cancle',
    )
    # return RedirectResponse(checkout_session["url"])
    return {"sessionId": checkout_session["id"], 'message': checkout_session["url"]}

@app.post("/webhook")
async def webhook_received(request: Request, stripe_signature: str = Header(None)):
    webhook_secret = "we_1NXfnWFm689lJVNLqsUTbAQn"
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=webhook_secret
        )
        event_data = event['data']
    except Exception as e:
        return {"error": str(e)}
    
    print(event_data)

    event_type = event['type']
    if event_type == 'checkout.session.completed':
        print('checkout session completed')
    elif event_type == 'invoice.paid':
        print('invoice paid')
    elif event_type == 'invoice.payment_failed':
        print('invoice payment failed')
    else:
        print(f'unhandled event: {event_type}')
    
    return {"status": "success"}

# @payment_app.post("/create_stripe_test", tags=["payments_service"])
# #def check_qrcode(user_id: str = Depends(oauth2_utils.require_user)):
# async def create_stripe_test(request : Request):
#     try:
#         payload = await request.body()
#         my_json = payload.decode('utf8').replace("'", '"')
#         data = json.loads(my_json)
#         stripe.api_key = ENV.STRIPE_KEY

#         #รับจาก body price คือ จำนวนที่ลูกค้าใส่เงินมา
#         price = data["price"]
#         user_id = data["user_id"]
#         name = "pack"+str(price)
#         unit_price = price * 100
#         print(ENV.STRIPE_REDIRECT)
#         a=stripe.checkout.Session.create(
#             payment_method_types=['card'],

#             # or you can take multiple payment methods with
#             # payment_method_types=['card', 'promptpay', ...]
#             line_items=[{
#                 'price_data': {
#                 'currency': 'thb',
#                 'product_data': {
#                     'name': name,
#                 },
#                 'unit_amount': unit_price,

#                 },

#                 'quantity': 1,
#             }],
#             mode='payment',
#             client_reference_id=user_id,
#             success_url=ENV.STRIPE_REDIRECT,
#             #after_completion={"type": "redirect", "redirect": {"url": ENV.STRIPE_REDIRECT}},
#             cancel_url='https://example.com/cancel',
#         )
#         return {"status" : 200 ,'message': a["url"]}
#     except Exception as e:
#         message = {"message" : str(e), "TypeError:" : type(e).name,"file_name" : file,  "line" : e.traceback.tb_lineno}
#         print("payment_check_qrcode error", message)

#         raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},)

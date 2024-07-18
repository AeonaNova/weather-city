import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, Query, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from database import SessionLocal
from models import User, Search
from fastapi.staticfiles import StaticFiles

load_dotenv(dotenv_path=".env")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./static"), name="static")
templates = Jinja2Templates(directory="./templates")

API_KEY = os.environ.get('API_KEY')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if user_id:
        last_search = db.query(Search).filter(Search.user_id == user_id).order_by(Search.id.desc()).first()
        if last_search:
            return templates.TemplateResponse("base.html", {"request": request, "last_search": last_search.city.capitalize()})
    return templates.TemplateResponse("base.html", {"request": request})


@app.post("/")
def get_weather(request: Request, city: str = Form(...), db: Session = Depends(get_db)):
    if not city.strip():
        error_message = 'Пожалуйста, введите название города.'
        return templates.TemplateResponse("base.html", {"request": request, "error": error_message})
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    data = response.json()
    print(city)

    if data['cod'] == 200:
        weather_data = {
            'city': data['name'].capitalize(),
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description']
        }

        user_id = request.cookies.get("user_id")
        if not user_id:
            user = User()
            db.add(user)
            db.commit()
            user_id = user.id
        else:
            user = db.query(User).filter(User.id == user_id).first()
        city = city.capitalize()
        search = Search(user_id=user.id, city=city)
        db.add(search)
        db.commit()
        response = templates.TemplateResponse("result.html", {"request": request, "weather": weather_data})
        response.set_cookie(key="user_id", value=str(user_id))
        return response

    else:
        error_message = 'Ошибка при получении данных о погоде.'
        return templates.TemplateResponse("base.html", {"error": error_message})


@app.get("/api/search-stats")
def search_stats(request: Request, db: Session = Depends(get_db)):
    search_stats = db.query(Search.city, func.count(Search.city).label('count')).group_by(Search.city).all()
    data = {city: count for city, count in search_stats}
    response = templates.TemplateResponse("statistics.html", {"request": request, "data": data})
    return response

@app.get("/cities/")
async def get_cities(q: str = Query(default="", min_length=0), db: Session = Depends(get_db)):
    cities = db.query(Search.city).filter(Search.city.like(f'%{q}%')).distinct().all()
    filtered_cities = [city[0].capitalize() for city in cities if q.lower() in city[0].lower()]
    return JSONResponse(content={"cities": filtered_cities}, media_type="application/json")


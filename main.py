from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import json

app = FastAPI()

# 정적 파일 설정 (CSS, 이미지, JS 등)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# TMDB API 설정
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2YTZiNGFkOWU0NDZkNWUyZGYzMzRiYWI1NmQ3ZDA5ZSIsIm5iZiI6MTc1ODc4MjI5NS4zMzc5OTk4LCJzdWIiOiI2OGQ0ZTM1NzE0NGZkNzdkYTAxOWRiM2UiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.PGPIr4xbTCFngrOyLKJE-OhaZhhwFYQSngoq1nuCcl0"
BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/movie/{movie_id}", response_class=HTMLResponse)
async def get_movie(request: Request, movie_id: int):
    movie_url = f"{BASE_URL}/movie/{movie_id}?language=ko-KR"
    videos_url = f"{BASE_URL}/movie/{movie_id}/videos?language=en-US"
    
    try:
        # 영화 기본 정보 가져오기
        movie_response = requests.get(movie_url, headers=headers)
        movie_response.raise_for_status()
        movie_data = movie_response.json()
        
        # 영화 동영상 정보 가져오기
        videos_response = requests.get(videos_url, headers=headers)
        videos_response.raise_for_status()
        videos_data = videos_response.json()
        
        # YouTube 예고편 필터링 (Trailer, Teaser)
        trailers = [video for video in videos_data.get('results', []) 
                   if video.get('site') == 'YouTube' and 
                   video.get('type') in ['Trailer', 'Teaser']]
        
        movie_data['trailers'] = trailers
        
        return templates.TemplateResponse("movie_detail.html", {"request": request, "movie": movie_data})
    except requests.exceptions.RequestException as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})

@app.get("/search", response_class=HTMLResponse)
async def search_movies(request: Request, q: str = ""):
    if not q:
        return templates.TemplateResponse("index.html", {"request": request, "error": "검색어를 입력해주세요."})
    
    url = f"{BASE_URL}/search/movie?query={q}&language=ko-KR"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() #애러 체크
        search_results = response.json()
        return templates.TemplateResponse("search_results.html", {
            "request": request, 
            "results": search_results['results'], 
            "query": q
        })
    except requests.exceptions.RequestException as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})

@app.get("/popular", response_class=HTMLResponse)
async def popular_movies(request: Request):
    url = f"{BASE_URL}/movie/popular?language=ko-KR"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movies_data = response.json()
        return templates.TemplateResponse("popular.html", {"request": request, "movies": movies_data['results']})
    except requests.exceptions.RequestException as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})

# API 엔드포인트
@app.get("/api/movie/{movie_id}")
async def get_movie_api(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}?language=ko-KR"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:


        raise HTTPException(status_code=404, detail=str(e))
    
    #uvicorn main:app --reload --port 5000
from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from sqlalchemy.exc import IntegrityError
from typing import List

from clients.db import create_db
from models.db import User, Post

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SessionLocal = create_db()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=dict)
def create_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = User(username=username, email=email, password=password)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": f"User {user.username} created successfully!"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists.")

@app.post("/posts/", response_model=dict)
def create_post(title: str = Form(...), content: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    post = Post(title=title, content=content, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"message": f"Post '{post.title}' created successfully!"}

@app.get("/users/", response_model=List[dict])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "email": user.email} for user in users]

@app.get("/posts/", response_model=List[dict])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return [{"id": post.id, "title": post.title, "content": post.content, "user": {"id": post.user.id, "username": post.user.username}} for post in posts]

@app.get("/users/{id}/posts", response_model=List[dict])
def get_user_posts(id: int, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.user_id == id).all()
    return [{"id": post.id, "title": post.title, "content": post.content} for post in posts]

@app.put("/users/{id}/email", response_model=dict)
def update_user_email(id: int, email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.email = email
    db.commit()
    return {"message": f"User {user.username}'s email updated to {email}."}

@app.put("/posts/{post_id}/content", response_model=dict)
def update_post_content(post_id: int, content: str = Form(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    post.content = content
    db.commit()
    return {"message": f"Post '{post.title}' content updated."}

@app.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    db.delete(post)
    db.commit()
    return {"message": f"Post '{post.title}' deleted."}

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} and their posts deleted."}

@app.get("/users/create", response_class=HTMLResponse)
def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.get("/posts/create", response_class=HTMLResponse)
def create_post_form(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("create_post.html", {"request": request, "users": users})

@app.get("/users/list", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("list_users.html", {"request": request, "users": users})

@app.get("/posts/list", response_class=HTMLResponse)
def list_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return templates.TemplateResponse("list_posts.html", {"request": request, "posts": posts})

@app.get("/users/{id}/edit", response_class=HTMLResponse)
def edit_user_form(id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@app.get("/posts/{id}/edit", response_class=HTMLResponse)
def edit_post_form(id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})

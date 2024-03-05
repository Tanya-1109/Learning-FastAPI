from fastapi import FastAPI,Depends,status, Response, HTTPException
from . import schemas,models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
from .hashing import Hash

app = FastAPI()


models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post('/blog', status_code = status.HTTP_201_CREATED,tags=['Blogs'])
def create(request: schemas.Blog,db:Session = Depends(get_db)):
    new_blog = models.Blog(title = request.title, body= request.body, user_id = 1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.delete('/blog/{id}', status_code = status.HTTP_204_NO_CONTENT,tags=['Blogs'])
def destroy(id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=404, detail="Blog not found") 
    blog.delete(synchronize_session = False)
    db.commit()
    return 'done'

@app.put('/blog/{id}',status_code = status.HTTP_202_ACCEPTED,tags=['Blogs'])
def update(id, request: schemas.Blog,db:Session = Depends(get_db)):
    # Convert Pydantic model to dictionary
    updated_data = request.dict(exclude_unset=True)
    # Update the database entry
    db_blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    for key, value in updated_data.items():
        setattr(db_blog, key, value)
    db.commit()
    return 'Updated successfully'

@app.get('/blog', response_model = List[schemas.ShowBlog],tags=['Blogs'])
def all(db: Session = Depends(get_db)):
    blogs =db.query(models.Blog).all()
    return blogs

@app.get('/blog/{id}', status_code = 200, response_model = schemas.ShowBlog,tags=['Blogs'])
def show(id,response:Response,db: Session= Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail =f"Blog with the id {id} not found")
       # response.status_code = status.HTTP_404_NOT_FOUND
       # return {'detain':f"Blog with the id {id} not found"}
    return blog

@app.post('/user',response_model=schemas.ShowUser,tags=['Users'])
def create_user(request:schemas.User,db:Session = Depends(get_db)):
    
    new_user = models.User(name = request.name, email= request.email, password = Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user/{id}',response_model = schemas.ShowUser, tags=['Users'])
def get_user(id:int ,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail =f"User with the id {id} not found")
    return user

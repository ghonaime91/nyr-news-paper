from app import (
     app,
     bcrypt

) 
import re
from app.models import *
from flask import (
   render_template,
   redirect,
   request,
   session,
   url_for,
   flash
)

from werkzeug.utils import secure_filename
import re,os,random

# function to validate an email
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False


@app.route("/")
def index():
     header_subjects = Article.query.filter(
          Article.is_approved==True
          ).order_by(
          Article.created_at.desc()
          ).limit(2).all()
     rest_subjects = Article.query.filter(
          Article.is_approved==True
          ).order_by(
          Article.created_at.desc()
          ).offset(2).limit(6).all()
     end_subjects = Article.query.filter(
          Article.is_approved==True
          ).order_by(
          Article.created_at.desc()
          ).offset(8).limit(2).all()
     return render_template(
          "main/index.html",
          header_subjects=header_subjects,
          rest_subjects=rest_subjects,
           end_subjects=end_subjects
             )


@app.route("/categories/<cat_id>/subjects")
def subjects_by_categories(cat_id):
     subjects = Article.query.filter(
          Article.category_id == cat_id
          ).filter(
          Article.is_approved==True
          ).order_by(
          Article.created_at.desc()
          ).all()


     return render_template("main/subject_category.html",subjects=subjects)



@app.route("/about")
def about():
     return render_template ("main/about.html")


@app.route("/chatbot")
def chatbot():
     return render_template ("main/chatbot.html")


@app.route("/login",methods=["GET","POST"])
def login():
     if 'user' in session:
          return redirect(url_for("index"))
     
     if request.method == 'POST':
          login_data = request.form.to_dict()

          # check for empty inputs
          if login_data['email'] == '' or login_data['password'] == '':
               flash("من فضلك ادخل الايميل وكلمة المرور!","danger")
               return redirect(url_for("login"))
          
          # check if user exist
          user = User.query.filter(User.email == login_data['email']).first()

          # if no user with this email
          if not user:
               flash ("من فضلك تأكد من الايميل ",'danger')
               return redirect(url_for("login"))
          
          # if wrong password
          if not bcrypt.check_password_hash(user.password, login_data['password']):
              flash("من فضلك تأكد من كلمة المرور", 'danger')
              return redirect(url_for("login"))
          
          if not user.is_active:
               flash("حسابك في انتظار التفعيل من قبل المدير",'danger')
               return redirect(url_for("login"))
          
          session['user'] = {
               "id"    : user.id,
               "first_name":user.first_name ,
               "name"  : f"{user.first_name} {user.last_name}",
               "email" : user.email,
               "role"  :user.role.title,
          }

          flash( f"مرحبا بعودتك يا  {session['user']['name']}", 'success')  
          return redirect(url_for("index"))
     
     return render_template("main/login.html")


@app.route("/signup", methods=['GET','POST'])
def signup():
     if "user" in session:
          return redirect(url_for("index"))
     error=''
     # get all roles except admin
     roles = Role.query.filter(Role.title !="admin" ).all()
     role_ids = [role.id for role in roles]

     # on form submit
     if request.method == 'POST':
          form_data = request.form.to_dict()

          # check for empty inputs
          for key in form_data:
               if form_data[key].strip() == '':
                    error='empty input'
                    break

          # check for email unique or not
          email_to_check = User.query.filter(
               User.email == form_data['email']
               ).first()
         
          if email_to_check:
               error = 'used email'
          if not validate_email(form_data['email']):
               error='invalid email'

          # if any empty input          
          if error == 'empty input':
               return render_template(
                    "main/signup.html",
                    error     = error,
                    form_data = form_data,
                    roles     = roles
                    )   
                
          # if invalid email
          if error == 'invalid email':
               return render_template(
                    "main/signup.html",
                    error     = error,
                    form_data = form_data,
                    roles     = roles
                    ) 
          
          # if email is used
          if error == 'used email':
               return render_template(
                    "main/signup.html",
                    error     = error,
                    form_data = form_data,
                    roles     = roles
                    )   
           
          # validate roles
          user_role = int(form_data['user_role'])
          if user_role not in role_ids:
               error = 'role error'

          # if role is not valid
          if error == 'role error':
               return render_template(
                    "main/signup.html",
                    error     = error,
                    form_data = form_data,
                    roles     = roles
                    )  

          # if no error hash the password
          hashed_password = bcrypt.generate_password_hash(
               form_data['password']
               ).decode('utf-8')
          # create a new user
          user = User(
               first_name = form_data['first_name'],
               last_name  = form_data['last_name'],
               email      = form_data['email'],
               password   = hashed_password,
               role_id    = form_data['user_role']
               )
          db.session.add(user)
          db.session.commit()

          flash('تم التسجيل بنجاح ولكن حسابك في انتظار موافقة مدير الموقع',"success")
          return render_template("main/login.html")
     

     return render_template(
          "main/signup.html", roles=roles
          )


@app.route("/signout")
def signout():
     session.clear()
     return redirect(url_for("login"))


@app.route("/subjects/all/<sub_id>", methods=['GET', 'POST'])
def show_one_subject(sub_id):
    article = Article.query.get_or_404(sub_id)
    if not article.is_approved:
         flash("الموضوع في انتظار الموافقة على النشر من قبل المدير",'warning')
         return redirect(url_for("index"))
    comments = Comment.query.filter_by(article_id=sub_id).order_by(Comment.created_at).all()
    
    if request.method == 'POST':
        # التحقق من تسجيل الدخول
        if 'user' not in session:
            flash('يجب تسجيل الدخول لتتمكن من إضافة تعليق', 'danger')
            return redirect(url_for('login'))  # توجيه المستخدم إلى صفحة تسجيل الدخول
        
        content = request.form.get('content')
        
        if content:
            new_comment = Comment(user_id=session['user']['id'], article_id=sub_id, content=content)
            db.session.add(new_comment)
            db.session.commit()
            flash('تمت إضافة التعليق بنجاح', 'success')
            return redirect(url_for('show_one_subject', sub_id=sub_id))
        else:
            flash('يجب إدخال محتوى التعليق', 'danger')
    
    return render_template("main/show_subject.html", article=article, comments=comments)



@app.route("/author/subjects")
def show_my_subjects():
     # التحقق من تسجيل الدخول
     if 'user' not in session or session.get('user')['role'] != 'author' :
          return redirect(url_for('login'))  
     
     subjects = Article.query.filter(
          Article.author_id == int(session.get("user")['id']
     )).all()

     return render_template("main/show_my_subjects.html", subjects=subjects)


@app.route("/user/comments")
def show_my_comments():
     # التحقق من تسجيل الدخول
     if 'user' not in session  :
          return redirect(url_for('login'))  
     
     comments = Comment.query.filter(
          Comment.user_id == int(session.get("user")['id']
     )).all()

     return render_template("main/show_my_comments.html", comments=comments)


@app.route("/user/comments/delete/<comm_id>")
def delete_my_comment(comm_id):
     # التحقق من تسجيل الدخول
     if 'user' not in session  :
          return redirect(url_for('login'))  
     
     comment = Comment.query.get_or_404(comm_id)
     if not comment.user_id == session.get("user")['id']:
          flash("غير مصرح بالدخول",'success')
          return redirect(url_for("show_my_comments"))
     db.session.delete(comment)
     db.session.commit()
     flash("تم حذف التعليق بنجاح",'success')
     return redirect(url_for("show_my_comments"))


# function to get all categories
def get_categories():
    categories = Category.query.all()
    return categories




@app.route("/author/subjects/add",methods=['GET','POST'])
def author_add_subject():
     # التحقق من تسجيل الدخول
     if 'user' not in session or session.get('user')['role'] != 'author' :
          return redirect(url_for('login'))  
     
     error = False
     categories = get_categories()
   

     if request.method == "POST":
          form_data    = request.form.to_dict()

          for input in form_data:
               if form_data[input].strip() == '':
                    error='empty input'
                    break

          if error == 'empty input':
               flash("يجب ادخال كل من العنوان والمحتوى","danger")
               return redirect(request.url)

               
          # if there an image
          if  request.files.get("image",None):
               image = request.files["image"]
               image_name = secure_filename(image.filename)
               random_number = random.randint(1, 1000000)
               image_name = f"{random_number}_{image_name}"
               images_folder = os.path.join(app.static_folder, "img/uploads/")
               #os.makedirs(images_folder, exist_ok=True)
               image.save(os.path.join(images_folder, image_name))
               image_url = url_for("static", filename=f"img/uploads/{image_name}", _external=True)
               form_data['image'] = image_name

          # if there an audio
          if request.files.get("audio",None):
               audio = request.files["audio"]
               audio_name = secure_filename(audio.filename)
               random_number = random.randint(1, 1000000)
               audio_name = f"{random_number}_{audio_name}"
               audio_folder = os.path.join(app.static_folder, "audio/uploads/")
               #os.makedirs(images_folder, exist_ok=True)
               audio.save(os.path.join(audio_folder, audio_name))
               audio_url = url_for("static", filename=f"audio/uploads/{audio_name}", _external=True)
               form_data['audio'] = audio_name
          
          form_data['author'] = session['user']['id']
          article = Article(

               title       = form_data.get('title'),
               content     = form_data.get('content'),
               category_id = form_data.get('category_id'),
               author_id   = form_data.get('author'),
               image       = form_data.get("image","none"),
               audio       = form_data.get("audio","none"),
          )

          db.session.add(article)
          db.session.commit()
          flash("تم اضافة الموضوع ولكنه في انتظار موافقة المدير", 'success')      
          return redirect(url_for("show_my_subjects"))
     return render_template("main/author_add_subject.html", categories=categories)




@app.route("/author/subjects/update/<sub_id>",methods=["GET","POST"])
def author_update_subject(sub_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'author':
        return redirect(url_for("index"))
    
    # get the article by its ID

    article = Article.query.get_or_404(sub_id)

    if not article.author_id == session.get('user')['id']:
         flash("غير مصرح بالدخول",'danger')
         return redirect("show_my_subjects")
    
    categories = get_categories()
    
    if request.method == "POST":
        form_data = request.form.to_dict()
        
        for input in form_data:
            if form_data[input].strip() == '':
                flash("يجب ادخال جميع الحقول", "danger")
                return redirect(request.url)
        
        # if there is a new image
        if request.files.get("image", None):
            image = request.files["image"]
            image_name = secure_filename(image.filename)
            random_number = random.randint(1, 1000000)
            image_name = f"{random_number}_{image_name}"
            images_folder = os.path.join(app.static_folder, "img/uploads/")
            
            # delete the old image if exists
            if article.image != "none":
                old_image_path = os.path.join(images_folder, article.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            image.save(os.path.join(images_folder, image_name))
            form_data['image'] = image_name
        # if there is no new image
        else:
            form_data['image'] = article.image
        
        # if there is a new audio
        if request.files.get("audio", None):
            audio = request.files["audio"]
            audio_name = secure_filename(audio.filename)
            random_number = random.randint(1, 1000000)
            audio_name = f"{random_number}_{audio_name}"
            audio_folder = os.path.join(app.static_folder, "audio/uploads/")
            
            # delete the old audio if exists
            if article.audio != "none":
                old_audio_path = os.path.join(audio_folder, article.audio)
                if os.path.exists(old_audio_path):
                    os.remove(old_audio_path)
            
            audio.save(os.path.join(audio_folder, audio_name))
            form_data['audio'] = audio_name
        # if there is no new audio
        else:
            form_data['audio'] = article.audio
        
        # update the article with the new data
        article.title = form_data['title']
        article.is_approved = False
        article.content = form_data['content']
        article.category_id = form_data['category_id']
        article.image = form_data.get("image", "none")
        article.audio = form_data.get("audio", "none")
        
        db.session.commit()
        flash("تم تحديث المقالة ولكن التغيير في انتظار الاعتماد من المدير", "success")
        return redirect(url_for("show_my_subjects"))
    
    return render_template(
        "main/author_update_subject.html",
        article=article,
        categories=categories
        )



@app.route("/search")
def search():
    search_key = request.args.get("q")
    results = Article.query.filter(
         Article.title.ilike(
         f"%{search_key}%"
         )).all()
    results_num = len(results)
    return render_template("main/search_results.html", results=results,num=results_num)






@app.errorhandler(500)
def internal_server_error(e):
    # قم بتنفيذ الإجراءات المناسبة للتعامل مع الخطأ هنا
    # على سبيل المثال، يمكنك إظهار صفحة خاصة لخطأ 500 للمستخدم
    return redirect(url_for("index"))




from app import app, bcrypt
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





# users module

@app.route("/users")
def show_users():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@app.route("/activate/<user_id>")
def activate(user_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash("تم تفعيل المستخدم بنجـاح","success")
    return redirect(url_for("show_users"))


@app.route("/deactivate/<user_id>")
def deactivate(user_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    user = User.query.get_or_404(user_id)
    if user.role_id == 1:
        flash("لا يمكنك الغاء تفعيل المدير","warning")
        return redirect(url_for("show_users"))
    user.is_active = False
    db.session.commit()
    flash("تم الغاء تفعيل المستخدم بنجـاح","success")
    return redirect(url_for("show_users"))


@app.route("/users/delete/<user_id>")
def delete_user(user_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    user = User.query.get_or_404(user_id)

    if user.role_id == 1:
        flash("لا يمكنك حذف حساب المدير","warning")
        return redirect(url_for("show_users"))
    
    db.session.delete(user)
    db.session.commit()

    flash("تم حذف المستخدم بنجـاح","success")
    return redirect(url_for("show_users"))



@app.route("/users/add", methods=['GET','POST'])
def add_user():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    error=''
    # get all roles except admin
    roles = Role.query.all()
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

        flash('تم إضافة مستخدم جديد بنجاح',"success")
        return redirect(url_for("show_users"))
    
    return render_template(
    "admin/add_user.html", roles=roles
    )




@app.route("/users/update/<user_id>", methods=['GET','POST'])
def update_user(user_id):
    roles = Role.query.all()
    user = User.query.get_or_404(user_id)
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    # on form submit
    if request.method == 'POST':
        form_data      = request.form.to_dict()
        data_to_update = {}

        # enshure no empty inputs
        for val in form_data:
            form_data[val].strip()

        # the new data
        for val in form_data:
            if not form_data[val] == '':
                data_to_update[val] = form_data[val]

        # if no error hash the password
                     
        for key, value in data_to_update.items():
            setattr(user, key, value)

        if 'password' in data_to_update:
            hashed_password = bcrypt.generate_password_hash(
            data_to_update['password']
            ).decode('utf-8')
            user.password = hashed_password

        if 'user_role' in data_to_update:
            user.role_id = data_to_update['user_role']    


        
        db.session.commit()
        flash('تم تحديث بيانات  المستخدم بنجاح',"success")
        return redirect(url_for("show_users"))

    return render_template("admin/update_user.html", user=user,roles=roles)

    
    


@app.route("/secret123147159/role", methods=['GET', 'POST'])
def secret_role_create():
    if request.method == 'POST':
        data = request.form.get("title").strip()
        role = Role(title=data)
        db.session.add(role)
        db.session.commit()
        flash("تم اضافة الدور بنجاح")
        return redirect(url_for("login"))


    return render_template("admin/secret_role.html" )




@app.route("/secret123147159/admin", methods=['GET', 'POST'])
def secret_admin_create():
    error=''
    # get all roles except admin
    roles = Role.query.all()

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
                "admin/secret.html",
                error     = error,
                form_data = form_data,
                roles     = roles
                )   
            
        # if invalid email
        if error == 'invalid email':
            return render_template(
                "admin/secret.html",
                error     = error,
                form_data = form_data,
                roles     = roles
                ) 
        
        # if email is used
        if error == 'used email':
            return render_template(
                "admin/secret.html",
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
            role_id    = form_data.get('user_role',1),
            is_active = True
            )
        db.session.add(user)
        db.session.commit()

        flash('تم إضافة مستخدم جديد بنجاح',"success")
        return redirect(url_for("login"))

    return render_template(
    "admin/secret.html", roles=roles
    )


#categories module

# function to get all categories
def get_categories():
    categories = Category.query.all()
    return categories

# to make categories accessable in all app
@app.context_processor
def inject_categories():
    return dict(get_categories=get_categories)



@app.route("/categories")
def show_categories():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    categories = get_categories()

    return render_template(
        "admin/categories.html",
          categories=categories
        )


# delete category
@app.route("/categories/delete/<cat_id>")
def delete_category(cat_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    category = Category.query.get_or_404(cat_id)
  
    if  len(list(category.articles)) >  0:
        flash("لايمكنك حذف هذه الفئة لأنها تحتوي مواضيع","danger")
        return redirect(url_for("show_categories"))

    db.session.delete(category)
    db.session.commit()

    flash("تم حذف الفئة بنجـاح","success")
    return redirect(url_for("show_categories"))


# add category
@app.route("/categories/add",methods=['GET','POST'])
def add_category():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    if request.method == 'POST':
        category_title = request.form.get('title').strip()
        if category_title == '':
            flash("من فضلك ادخل اسم الفئة",'danger')
            return redirect(url_for("add_category"))
        
        category = Category(title=category_title)
        db.session.add(category)
        db.session.commit()
        flash("تم إضافة الفئة بنجـاح",'success')
        return redirect(url_for("show_categories"))

    return render_template("admin/add_category.html")


# update category 
@app.route("/categories/update/<cat_id>",methods=['GET','POST'])
def update_category(cat_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    category = Category.query.get_or_404(cat_id)
    if request.method == "POST":
        category_title = request.form.get('title').strip()
        if category_title == '' or category_title == category.title:
            flash("لم يتم وضع اسم جديد للفئة",'warning')
            return redirect(url_for("update_category",cat_id=category.id))
        
        category.title = category_title
        db.session.commit()
        flash("تم تحديث اسم الفئة بنجاح", 'success')
        return redirect(url_for("show_categories"))        


    return render_template("admin/update_category.html", category=category)




# subjects module
@app.route("/subjects/add",methods=['GET','POST'])
def add_subject():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    error = False
    categories = get_categories()
    if(len(categories) < 1):
        flash("برجاء ادخل الفئات اولا",'danger')
        return redirect(url_for("add_category"))

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
            is_approved = True,
            category_id = form_data.get('category_id'),
            author_id   = form_data.get('author'),
            image       = form_data.get("image","none"),
            audio       = form_data.get("audio","none"),
        )

        db.session.add(article)
        db.session.commit()
        flash("تم اضافة الموضوع بنجاح", 'success')      
        return redirect(url_for("show_subjects"))
    
    return render_template("admin/subjects/add_subject.html", categories=categories)


@app.route("/subjects")
def show_subjects():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    subjects = Article.query.order_by(Article.created_at.desc()).all()
    return render_template("admin/subjects/show_subjects.html",subjects=subjects)


@app.route("/subjects/<sub_id>", methods=['GET', 'POST'])
def see_one_subject(sub_id):
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    article = Article.query.get_or_404(sub_id)
    comments = Comment.query.filter_by(article_id=sub_id).order_by(Comment.created_at.desc()).all()

    
    return render_template("main/show_subject.html", article=article, comments=comments)



@app.route("/subjects/delete/<sub_id>")
def delete_subject(sub_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    article = Article.query.get_or_404(sub_id)
    # if there is an image
    if article.image != 'none':
        image_path = os.path.join(app.static_folder, f"img/uploads/{article.image}")
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # if there is an audio
    if article.audio != 'none':
        audio_path = os.path.join(app.static_folder, f"audio/uploads/{article.audio}")
        if os.path.exists(audio_path):
            os.remove(audio_path)

    db.session.delete(article)
    db.session.commit()
    flash("تم حذف الموضوع بنجاح",'success')
    return redirect(url_for("show_subjects"))






@app.route("/subjects/update/<sub_id>", methods=['GET', 'POST'])
def update_subject(sub_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    # get the article by its ID
    article = Article.query.get_or_404(sub_id)
    
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
        article.content = form_data['content']
        article.category_id = form_data['category_id']
        article.image = form_data.get("image", "none")
        article.audio = form_data.get("audio", "none")
        
        db.session.commit()
        flash("تم تحديث المقالة بنجاح", "success")
        return redirect(url_for("show_subjects"))
    
    return render_template(
        "admin/subjects/update_subject.html",
        article=article,
        categories=categories
        )



@app.route("/subjects/approve/<sub_id>")
def approve_subject(sub_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    subject = Article.query.get_or_404(sub_id)
    subject.is_approved = True
    db.session.commit()
    flash("تم اعتماد الموضوع للنشر ",'success')
    return redirect(url_for("show_subjects"))


@app.route("/subjects/disallow/<sub_id>")
def disallow_subject(sub_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    subject = Article.query.get_or_404(sub_id)
    subject.is_approved = False
    db.session.commit()
    flash("تم الغاء اعتماد الموضوع  ",'success')
    return redirect(url_for("show_subjects"))

@app.route("/comments")
def show_comments():
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    comments = Comment.query.order_by(Comment.created_at.desc()).all()

    return render_template("admin/show_comments.html",comments=comments)



@app.route("/comments/delete/<comm_id>")
def delete_comment(comm_id):
    # check if user logged in and is admin
    if not 'user' in session or session.get('user')['role'] != 'admin':
        return redirect(url_for("index"))
    
    comment = Comment.query.get_or_404(comm_id)
    db.session.delete(comment)
    db.session.commit()
    flash("تم حذف التعليق بنجاح",'success')
    return redirect(url_for("show_comments"))

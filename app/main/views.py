#!/usr/bin/env python
# encoding:utf-8

from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user

from app.main import main
from flask.ext.sqlalchemy import get_debug_queries
from app.main.forms import EditProfileForm, PostForm
from app.models import db, User, Post, Tag, PostTags

__author__ = 'zhangmm'


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['ZBLOG_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning('Slow query: %s\nParameters: %s\nDuration: %s\nContext: %s' %
                                       query.statement, query.parameters, query.duration, query.context)
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZBLOG_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    tags = Tag.query.all()
    return render_template('index.html', posts=posts, pagination=pagination, tags=tags, show_all=False)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZBLOG_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    form = EditProfileForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<title>')
def post(title):
    post = Post.query.filter_by(url_title=title).first()
    if not post:
        abort(404)
    return render_template('post.html', posts=[post, ], show_all=True)


@main.route('/tag/<name>')
def tag(name):
    query = Post.query.join(PostTags, PostTags.post_id == Post.id) \
        .join(Tag, Tag.id == PostTags.tag_id).filter(Tag.name == name)
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZBLOG_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    tags = Tag.query.all()
    return render_template('index.html', posts=posts, pagination=pagination, tags=tags, show_all=False)


@main.route('/new-post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        # todo： add tags
        db.session.add(post)
        flash('The post has been added.')
        return redirect(url_for('post', title=post.url_title))
    return render_template('edit_post.html', form=form, is_new=True)


@main.route('/edit/<title>', methods=['GET', 'POST'])
@login_required
def edit(title):
    post = Post.query.filter_by(url_title=title).first()
    if not post:
        abort(404)
    if current_user != post.author:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('post', title=post.url_title))
    form.body.data = post.body
    form.title.data = post.title
    return render_template('edit_post.html', form=form, is_new=False)
    

@main.route('/about-me')
def about_me():
    user = User.query.first()
    return render_template('about_me.html', user=user)

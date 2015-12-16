#!/usr/bin/env python
# encoding:utf-8

from flask import render_template, redirect, url_for, abort, flash, request, current_app
from flask.ext.login import login_required, current_user
from sqlalchemy import func
from app.main import main
from flask.ext.sqlalchemy import get_debug_queries
from app.main.forms import EditProfileForm, PostForm, TagForm
from app.models import db, User, Post, Tag, PostTags

__author__ = 'zhangmm'


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['ZBLOG_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning('Slow query: {0!s}\nParameters: {1!s}\nDuration: {2!s}\nContext: {3!s}'.format(*
                                       query.statement), query.parameters, query.duration, query.context)
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


@main.route('/user/<username>/edit', methods=['GET', 'POST'])
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
        flash('个人信息已更新.')
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


@main.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZBLOG_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('posts.html', posts=posts, pagination=pagination)


@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    post = Post()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.author = current_user
        db.session.add(post)
        db.session.commit()
        tag_ids = form.tags.data
        for tag_id in tag_ids:
            post_tags = PostTags(post_id=post.id, tag_id=tag_id)
            db.session.add(post_tags)
        flash('文章已发布.')
        return redirect(url_for('.post', title=post.url_title))
    return render_template('edit_post.html', form=form, is_new=True)


@main.route('/post/<title>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(title):
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
        for tag in post.tags:
            db.session.delete(tag)
        tag_ids = form.tags.data
        for tag_id in tag_ids:
            post_tags = PostTags(post_id=post.id, tag_id=tag_id)
            db.session.add(post_tags)
        flash('文章已更新.')
        return redirect(url_for('.post', title=post.url_title))
    form.title.data = post.title
    form.tags.data = [tag.id for tag in post.tags]
    form.body.data = post.body
    return render_template('edit_post.html', form=form, is_new=False)


@main.route('/post/<title>/delete', methods=['GET', 'POST'])
def delete_post(title):
    if request.method == 'GET':
        post = Post.query.filter_by(url_title=title).first()
        if not post:
            abort(404)
        return render_template('delete_post.html', post=post)
    if request.method == 'POST':
        post = Post.query.filter_by(url_title=title).first()
        if not post:
            abort(404)
        db.session.delete(post)
        PostTags.query.filter_by(post_id=post.id).delete()
        flash('文章已删除.')
        return redirect(url_for('.posts'))
    abort(404)


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


@main.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    form = TagForm()
    tag = Tag()
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.add(tag)
        flash('标签已添加')
    form.name.data = tag.name
    tags = db.session.query(Tag.name, func.count(Tag.name).label('post_count')).join(Tag.posts).group_by(
        Tag.name).all()
    return render_template('tags.html', tags=tags, form=form)


@main.route('/tag/<name>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(name):
    tag = Tag.query.filter_by(name=name).first()
    if not tag:
        abort(404)
    form = TagForm()
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.add(tag)
        flash('标签已更新.')
        return redirect(url_for('tag'))
    form.name.data = tag.name
    return render_template('edit_tag.html', form=form)


@main.route('/tag/<name>/delete', methods=['GET', 'POST'])
@login_required
def delete_tag(name):
    if request.method == 'GET':
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            abort(404)
        return render_template('delete_tag.html', tag=tag)
    if request.method == 'POST':
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            abort(404)
        db.session.delete(tag)
        PostTags.query.filter_by(tag_id=tag.id).delete()
        flash('标签已删除.')
        return redirect(url_for('.tags'))
    abort(404)


@main.route('/about-me')
def about_me():
    user = User.query.first()
    return render_template('about_me.html', user=user)

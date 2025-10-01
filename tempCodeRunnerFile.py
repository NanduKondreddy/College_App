from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt
)
from config import Config
from models import db, User, Course, Branch, Semester

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

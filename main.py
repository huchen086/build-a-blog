#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, cgi, jinja2, os, re

from string import letters
from google.appengine.ext import db
from datetime import datetime

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
    q = "SELECT * FROM Blog ORDER BY datetime_created DESC LIMIT {0} OFFSET {1}".format(limit, offset)
    blogs = db.GqlQuery(q)
    return blogs

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.StringProperty(required = True)
    datetime_created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Somethine went wrong.")

class Index(Handler):
    def get(self):
        self.redirect("/blog")

class Main(Handler):
    def get(self):
        blogs = get_posts(5, 0)
        t = jinja_env.get_template("list.html")
        content = t.render(blogs = blogs)
        self.response.write(content)

class AddPost(Handler):
    def render_blog_form(self, title="", body="", error=""):
        t = jinja_env.get_template("newpost.html")
        content = t.render(title = title, body = body, error = error)
        self.response.write(content)

    def get(self):
        self.render_blog_form()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = Blog(title = title, body = body)
            b.put()
            self.redirect("/blog/" + str(b.key().id()))
        else:
            error = "We need both a title and a body."
            self.render_blog_form(title, body, error)

class ViewPost(Handler):
    def get(self, id):
        id = int(id)
        b = Blog.get_by_id(id)
        t = jinja_env.get_template("blog.html")
        content = t.render(blog = b)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', Main),
    ('/newpost', AddPost),
    webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)

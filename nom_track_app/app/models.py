from nom_track_app.app import db
#
# ratings = db.Table('ratings',
#                    db.Column('user_id', db.String(80), db.ForeignKey('user.id'), primary_key=True),
#                    db.Column('rating_id', db.String(80), db.ForeignKey('rating.id'), primary_key=True)

class User(db.Model):
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    ratings = db.relationship('UserRating', backref = 'user', lazy='dynamic')

    def rate_food(self, food_source, rating):
        db.session.add(self)

        user_rating = self.ratings.filter_by(food_source=food_source).first()
        if not user_rating:
            user_rating = UserRating(food_source=food_source)
        user_rating.rating = rating

        self.ratings.append(user_rating)

        db.session.add(user_rating)
        db.session.commit()

        return user_rating

# class FoodSource(db.Model):
#     name = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

class UserRating(db.Model):
    __tablename__ = "user_ratings"
    id = db.Column(db.Integer, primary_key=True)
    food_source = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer)
    user_id = db.Column(db.String(80), db.ForeignKey('user.id'), nullable=False)


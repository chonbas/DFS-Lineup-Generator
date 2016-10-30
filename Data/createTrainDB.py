# import sqlalchemy
# from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
# from sqlalchemy.orm import relationship, sessionmaker
# from sqlalchemy.sql import and_
# from sqlalchemy.ext.declarative import declarative_base
# import pandas as pd
# import numpy as np

# DATA_SOURCE = ""

# # Week;Year;GID;Name;Pos;Team;h/a;Oppt;FD points;FD salary
# # week,year,name,team,opp,score,att,yds,avg,td,fum

# class RunningBack:
#     def __init__(self, ):
#         self.body = body
#         self.harassment = flag
#         self.is_twitter = is_twitter
#     def __repr__(self):
#         return'<%s, %d>' %(self.body, self.harassment)


# def parseDB(path):
#     comments = []
#     df = pd.read_csv(path, encoding="utf-8")
#     raw_data = df['body'].values
#     target = df['is_harassment'].values
#     twitter = df['is_twitter'].values
#     for i in xrange(len(raw_data)):
#         comments.append(TrainingComment(raw_data[i], int(target[i]), int(twitter[i])))
#     return comments

# def preseedTrain(comments):
#     Base = declarative_base()

#     class TrainComment(Base):
#         __tablename__ = 'comments'
#         id = Column(Integer, primary_key=True)
#         body = Column(Text)
#         harassment = Column(Integer)
#         is_twitter = Column(Integer)

#     train_db = create_engine('mysql+pymysql://foot:mlf00tb4ll@footballdata.#####.us-west-2.rds.amazonaws.com:3306/footdb?charset=utf8mb4', echo=False)
#     Base.metadata.drop_all(train_db)
#     Base.metadata.create_all(train_db)
#     Session = sessionmaker(bind=train_db)
#     session = Session()
#     for comment in comments:
#         new_comment = TrainComment(body=comment.body, harassment=comment.harassment)
#         session.add(new_comment)
#     session.commit()
#     session.close()


# preseedTrain(parseDB(DATA_SOURCE))
    
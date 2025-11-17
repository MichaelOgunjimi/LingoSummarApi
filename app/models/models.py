from datetime import datetime
from bson import ObjectId
from flask import g


def get_db():
    """Get database connection from Flask's g object."""
    from app import mongo_db
    if 'db' not in g:
        g.db = mongo_db
    return g.db


class Summary:
    """Summary document model using PyMongo."""
    
    collection_name = 'summary'
    
    def __init__(self, content, percentage, words, text_id, _id=None, created_at=None):
        self.id = _id
        self.content = content
        self.percentage = percentage
        self.words = words
        self.text_id = ObjectId(text_id) if isinstance(text_id, str) else text_id
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert Summary object to dictionary."""
        result = {
            'content': self.content,
            'percentage': self.percentage,
            'words': self.words,
            'text_id': self.text_id,
            'created_at': self.created_at
        }
        # Only include _id if it's not None
        if self.id is not None:
            result['_id'] = self.id
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create Summary object from dictionary."""
        return cls(
            content=data['content'],
            percentage=data.get('percentage'),
            words=data.get('words'),
            text_id=data['text_id'],
            _id=data.get('_id'),
            created_at=data.get('created_at')
        )
    
    def save(self):
        """Save summary to database."""
        db = get_db()
        if db is None:
            raise Exception("Database connection not available")
        
        collection = db[self.collection_name]
        summary_dict = self.to_dict()
        
        if self.id:
            # Update existing - exclude _id from update
            update_dict = {k: v for k, v in summary_dict.items() if k != '_id'}
            collection.update_one({'_id': self.id}, {'$set': update_dict})
        else:
            # Insert new
            result = collection.insert_one(summary_dict)
            self.id = result.inserted_id
        
        return self
    
    @classmethod
    def create_summary(cls, content, percentage, words, text):
        """
        Create and save a new Summary document.
        
        :param content: The content of the summary.
        :param percentage: The percentage of the original text covered.
        :param words: The word count of the summary.
        :param text: The Text object this summary is associated with.
        :return: The created Summary object.
        """
        summary = cls(
            content=content,
            percentage=percentage,
            words=words,
            text_id=text.id
        )
        summary.save()
        return summary
    
    @classmethod
    def find_by_text_id(cls, text_id):
        """Find all summaries for a given text."""
        db = get_db()
        if db is None:
            return []
        
        collection = db[cls.collection_name]
        text_oid = ObjectId(text_id) if isinstance(text_id, str) else text_id
        summaries = collection.find({'text_id': text_oid})
        return [cls.from_dict(s) for s in summaries]


class Text:
    """Text document model using PyMongo."""
    
    collection_name = 'text'
    
    def __init__(self, content, user_uid, uploaded_filename=None, percentage=None, 
                 _id=None, created_at=None, summary_ids=None):
        self.id = _id
        self.content = content
        self.user_uid = user_uid
        self.uploaded_filename = uploaded_filename
        self.percentage = percentage
        self.created_at = created_at or datetime.utcnow()
        self.summary_ids = summary_ids or []
        self._summaries = None  # Cache for summaries
    
    def to_dict(self):
        """Convert Text object to dictionary."""
        result = {
            'content': self.content,
            'user_uid': self.user_uid,
            'uploaded_filename': self.uploaded_filename,
            'percentage': self.percentage,
            'created_at': self.created_at,
            'summary_ids': self.summary_ids
        }
        # Only include _id if it's not None
        if self.id is not None:
            result['_id'] = self.id
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create Text object from dictionary."""
        return cls(
            content=data['content'],
            user_uid=data.get('user_uid'),
            uploaded_filename=data.get('uploaded_filename'),
            percentage=data.get('percentage'),
            _id=data.get('_id'),
            created_at=data.get('created_at'),
            summary_ids=data.get('summary_ids', [])
        )
    
    def save(self):
        """Save text to database."""
        db = get_db()
        if db is None:
            raise Exception("Database connection not available")
        
        collection = db[self.collection_name]
        text_dict = self.to_dict()
        
        if self.id:
            # Update existing - exclude _id from update
            update_dict = {k: v for k, v in text_dict.items() if k != '_id'}
            collection.update_one({'_id': self.id}, {'$set': update_dict})
        else:
            # Insert new
            result = collection.insert_one(text_dict)
            self.id = result.inserted_id
        
        return self
    
    @property
    def summaries(self):
        """Lazy load summaries for this text."""
        if self._summaries is None and self.id:
            self._summaries = Summary.find_by_text_id(self.id)
        return self._summaries or []
    
    @summaries.setter
    def summaries(self, value):
        """Set summaries cache."""
        self._summaries = value
    
    def add_summary(self, summary):
        """
        Add a Summary object to the Text's list of summaries.
        
        :param summary: The Summary object to add.
        :return: The Summary object.
        """
        if summary.id not in self.summary_ids:
            self.summary_ids.append(summary.id)
            self.save()
        return summary
    
    @classmethod
    def create_text(cls, content, user_uid, uploaded_filename=None, percentage=None):
        """
        Create and save a new Text document.
        
        :param content: The content of the text.
        :param user_uid: The user ID associated with this text.
        :param uploaded_filename: The name of the uploaded file, if any.
        :param percentage: An optional percentage associated with the text.
        :return: The created Text object.
        """
        text = cls(
            content=content,
            user_uid=user_uid,
            uploaded_filename=uploaded_filename,
            percentage=percentage
        )
        text.save()
        return text
    
    @classmethod
    def get_text_with_summaries(cls, text_id):
        """
        Fetch a Text by its ID, including all related Summary documents.
        
        :param text_id: The ID of the Text to fetch.
        :return: The Text object with its summaries if found, None otherwise.
        """
        text = cls.get_text_by_id(text_id)
        if text:
            text.summaries = Summary.find_by_text_id(text.id)
        return text
    
    @classmethod
    def get_texts_by_user(cls, user_uid):
        """
        Retrieve all Text documents associated with a specific user ID.
        
        :param user_uid: The user ID to filter Text documents by.
        :return: A list of Text objects associated with the user.
        """
        db = get_db()
        if db is None:
            return []
        
        collection = db[cls.collection_name]
        texts = collection.find({'user_uid': user_uid})
        return [cls.from_dict(t) for t in texts]
    
    @classmethod
    def get_text_by_id(cls, text_id):
        """
        Fetch a Text by its ID.
        
        :param text_id: The ID of the Text to fetch.
        :return: The Text object if found, None otherwise.
        """
        db = get_db()
        if db is None:
            return None
        
        collection = db[cls.collection_name]
        try:
            text_oid = ObjectId(text_id) if isinstance(text_id, str) else text_id
            text_data = collection.find_one({'_id': text_oid})
            return cls.from_dict(text_data) if text_data else None
        except Exception:
            return None
    
    @classmethod
    def get_all(cls):
        """
        Retrieve all Text documents.
        
        :return: A list of all Text objects.
        """
        db = get_db()
        if db is None:
            return []
        
        collection = db[cls.collection_name]
        texts = collection.find()
        return [cls.from_dict(t) for t in texts]


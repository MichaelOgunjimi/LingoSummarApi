from datetime import datetime

from app import db


class Summary(db.Document):
    content = db.StringField(required=True)
    percentage = db.FloatField()  # The percentage of the text that the summary covers
    words = db.IntField()  # Number of words in the summary
    created_at = db.DateTimeField(default=datetime.utcnow)
    text = db.ReferenceField('Text')  # Reference to the Text document

    @classmethod
    def create_summary(cls, content, percentage, words, text):
        """
        Create and save a new Summary document.

        :param content: The content of the summary.
        :param percentage: The percentage of the original text covered.
        :param words: The word count of the summary.
        :param text: The Text document this summary is associated with.
        :return: The created Summary document.
        """
        summary = cls(content=content, percentage=percentage, words=words, text=text)
        summary.save()
        return summary


class Text(db.Document):
    content = db.StringField(required=True)
    user_uid = db.StringField()  # This field is now nullable
    summaries = db.ListField(db.ReferenceField('Summary', reverse_delete_rule=db.PULL))
    created_at = db.DateTimeField(default=datetime.utcnow)
    uploaded_filename = db.StringField(required=False)  # The name of the uploaded file, if any
    percentage = db.FloatField(required=False)  # An optional percentage metric

    @classmethod
    def create_text(cls, content, user_uid, uploaded_filename=None, percentage=None):
        """
        Create and save a new Text document.

        :param content: The content of the text, either uploaded or directly written.
        :param user_uid: The user ID associated with this text.
        :param uploaded_filename: The name of the uploaded file, if the text was uploaded.
        :param percentage: An optional percentage associated with the text.
        :return: The created Text document.
        """
        text = cls(content=content, user_uid=user_uid, uploaded_filename=uploaded_filename, percentage=percentage)
        text.save()
        return text

    def add_summary(self, summary):
        """
        Add a Summary document to the Text document's list of summaries.

        :param summary: The Summary document to add.
        :return: The created Summary document.
        """
        self.summaries.append(summary)
        self.save()
        return summary

    @classmethod
    def get_text_with_summaries(cls, text_id):
        """
        Fetch a Text document by its ID, including all related Summary documents.

        :param text_id: The ID of the Text document to fetch.
        :return: The Text document along with its Summary documents if found, None otherwise.
        """
        text = cls.objects(id=text_id).first()
        if text:
            text.summaries = [summary for summary in Summary.objects(text=text)]
        return text

    @classmethod
    def get_texts_by_user(cls, user_uid):
        """
        Retrieve all Text documents associated with a specific user ID.

        :param user_uid: The user ID to filter Text documents by.
        :return: A list of Text documents associated with the user.
        """
        return cls.objects(user_uid=user_uid).all()

    @classmethod
    def get_text_by_id(cls, text_id):
        """
        Fetch a Text document by its ID.

        :param text_id: The ID of the Text document to fetch.
        :return: The Text document if found, None otherwise.
        """
        return cls.objects(id=text_id).first()

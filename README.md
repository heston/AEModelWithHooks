AEModelWithHooks
================

AEModelWithHooks provides automatic lifecycle hooks for App Engine models. This is a very
lightweight extension of AppEngine's standard python Model class.

Special "magic methods" may be defined in an inheriting class and will be run
automatically at various points in the model's life. Possible methods are:

* validate       : Run every time before the model is saved.
* before_create  : Run before the model is saved for the first time.
* after_create   : Run after the model is saved for the first time.
* before_save    : Run every time before the model is saved.
* after_save     : Run every time after the model is saved.
* after_get      : Run after the model is fetched from the datastore.

If an exception is raised in validate, before_create or before_save, the model will not
be saved.

Soft validation of models should be done in AEModelWithHooks.validate. If a field should
be marked as invalid, call ModelWithhooks.validation_error to add an error. If any
validation errors were registered, further hooks will not be executed, and the model
will not be saved.

"Soft" validation differs from "hard" validation in the sense that the model may still
be constructed with invalid data, but cannot be persisted to the datastore until it
passes validation. AppEngine's default validation will not allow an invalid model to be
instantiated at all.

If defined, the method "after_get" will only be run after the model class's "get" method
is called. It will not be run after "fetch" or "run" calls, for performance reasons.


Usage
=====

AEModelWithHooks inherits from AppEngine's python Model class.

To use it, simply inherit from AEModelWithHooks, and then create your model as you otherwise
would. To utilize any of the hooks, simply define those methods in your subclass.

Example
=======

Here's a working, if trivial, example.

```python
from AEModelWithHooks import AEModelWithHooks
from google.appengine.ext import db

class Person(AEModelWithHooks):
  name = db.StringProperty()
  nickname = db.StringProperty()
  
  def validate(self):
    """Validate fields before creating the model."""
    
    if not self.name:
      self.validation_error('name', 'Please enter your name.')
      
  def before_create(self):
    """"Munge some fields before actually saving the record"""
    
    if not self.nickname:
      self.nickname = self.name.split(' ')[0]
```

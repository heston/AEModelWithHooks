# License: Attribution-ShareAlike 3.0 Unported
#     http://creativecommons.org/licenses/by-sa/3.0/
#
# Author: Heston Liebowitz (https://github.com/heston)
#


from google.appengine.ext import db


class AEModelWithHooks(db.Model):
  """Provide hooks for managing the model lifecycle.

  Special "magic methods" defined in an inheriting class will be run
  automatically at various points in a model's life. Possible methods are:
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
  """

  def __init__(self, *args, **kwargs):
    super(AEModelWithHooks, self).__init__(*args, **kwargs)
    self.validation_errors = None


  def put(self, **kwargs):
    # If this is a new record
    if not self.is_saved():
      # before_create hooks
      if getattr(self, 'validate', None):
        self.validate()
      if self.validation_errors:
        return
      if getattr(self, 'before_create', None):
        self.before_create()
      if getattr(self, 'before_save', None):
        self.before_save()

      super(AEModelWithHooks, self).put(**kwargs)

      # after_create hook
      if getattr(self, 'after_save', None):
        self.after_save()
      if getattr(self, 'after_create', None):
        self.after_create()
    # If this is not a new record
    else:
      # before_save hooks
      if getattr(self, 'validate', None):
        self.validate()
      if self.validation_errors:
        return
      if getattr(self, 'before_save', None):
        self.before_save()

      super(AEModelWithHooks, self).put(**kwargs)

      # after_save hook
      if getattr(self, 'after_save', None) and self.is_saved():
        self.after_save()


  def validation_error(self, field, message):
    """Register a validation error on a field of this model.

    Args:
      field: The name of the field for which to register a validation error. This need
          not match up with the name of the model property. It may be anything you choose.
      message: The message relating to this validation error. This will often be what is
          shown in the UI.
    """

    error = {field: message}
    if self.validation_errors:
      self.validation_errors.append(error)
    else:
      self.validation_errors = [error]


  @classmethod
  def get(cls, keys, **kwargs):
    result = super(AEModelWithHooks, cls).get(keys, **kwargs)
    # after_get hook
    if getattr(result, 'after_get', None):
      result.after_get()
    return result

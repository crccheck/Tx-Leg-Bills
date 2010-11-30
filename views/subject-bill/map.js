function(doc) {
  for each (subject in doc.subject)
    emit(subject, doc._id);
}

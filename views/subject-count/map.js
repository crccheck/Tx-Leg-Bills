function(doc) {
  for each (subject in doc.subject)
    emit(subject.subject_id, 1);
}

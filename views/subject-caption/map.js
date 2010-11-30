function(doc) {
  for each (subject in doc.subject){
    emit(
      subject.subject_id, {'caption': doc.caption_text, 'url': doc.url}
    )
  }
}

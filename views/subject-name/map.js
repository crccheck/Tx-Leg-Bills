function(doc) {
    for each (subject in doc.subject)
        emit(
            subject.subject_id,
            subject.subject_name.toLowerCase()
              .replace( /([^,]+)(, (.*))?/, function(m,p1,p2,p3){ return p3 ? p3 + ' ' + p1 : m; })
              .replace( /(^|\W)([a-z])/g , function(m,p1,p2){ return p1.toLowerCase()+p2.toUpperCase(); } )
        )
}

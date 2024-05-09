just changed azure webapp to not require auth, so now we are relying on ZAuth and cookie setting header.

create a wss connction without being logged in with ZAuth- correct, it fails
create a wss connection when logged in with ZAuth- correct, it works

have tested that you can't create a wss connection without being logged in when using azure authentication required- correct, it fails
Have tested you can create a wss connection when logged in and Azure authentication required, correct, it works

Oh now I remember the whole issue with relying on ZAuth, it doesn't redirect back to the previous page after login. So we need to fix that.

app insights is broken for python 3.12

trying to see if printing hits the live logs

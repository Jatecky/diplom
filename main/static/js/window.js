let windowLinks = document.querySelectorAll('.window-link');
const body = document.querySelector('body');
let lockPadding = document.querySelectorAll(".lock-padding");
let windowPayButtons = document.querySelectorAll('.window-pay-button');
const windowPay = document.querySelector('.window-pay');
const buttonEndedOk = document.querySelector('.button-ended-ok');

var arrayScrVideo = [];

let unlock = true;

const timeout = 800;

function showWindowsEndedTickets() {
  const window = document.querySelector('.window-ended-tickets');
  windowOpen(window);
}

if(windowPay) {
  windowPay.addEventListener('submit', function(e){
    var req = new XMLHttpRequest()
    const input_id_film = document.getElementById('input_id_film');
    req.open('GET', 'check_film_payment?id=' + input_id_film.value.toString(), false);
    req.send();
    if(req.status === 200 && req.responseText === 'no') {
      showWindowsEndedTickets();
      e.preventDefault();
    }
  });
  if(buttonEndedOk) {
    buttonEndedOk.addEventListener('click', function(e) {
      const windowActive = document.querySelector('.window-ended-tickets');
      windowClose(windowActive);
    });
  }
}

function updateVars() {
  windowLinks = document.querySelectorAll('.window-link');
  lockPadding = document.querySelectorAll(".lock-padding");
  windowPayButtons = document.querySelectorAll('.window-pay-button');
}

function updateWindows(destroy=false) {

  if (windowLinks.length > 0) {
    for (let index = 0; index < windowLinks.length; index++) {
      const windowLink = windowLinks[index];
      if(destroy){
        windowLink.onclick = function(e){};
      } else {
        windowLink.onclick = function (e){
          const windowName= windowLink.getAttribute('href').replace('#', '');
          const curentWindow = document.getElementById(windowName);
          windowOpen(curentWindow);
          e.preventDefault();
        };
      }
    }
  }

    if (windowPayButtons.length > 0) {
      for(let index = 0; index < windowPayButtons.length; index++){
        const windowPayButton = windowPayButtons[index];
        if(destroy){
          windowPayButton.onclick = function(e){};
        } else {
          windowPayButton.onclick = function(e) {
            if(windowPay) {
              windowOpen(windowPay);
              e.preventDefault();
              const id = this.getAttribute('id').replace('btn_id_', '');
              const input_id_film = document.getElementById('input_id_film');
              input_id_film.setAttribute('value', id)
            }
          }
        } 

      }
    }

  const windowCloseIcon = document.querySelectorAll('.close-window');
  if (windowCloseIcon.length > 0) {
    for (let index = 0; index < windowCloseIcon.length; index++) {
      const el = windowCloseIcon[index];
      if(destroy){
        el.onclick = function(e){};
      } else {
        el.onclick = function (e) {
          windowClose(el.closest('.window'));
          e.preventDefault();
        };
      }
    }
  }

}

updateWindows();

function windowOpen(currentWindow) {
  if (currentWindow && unlock) {
    const windowActive = document.querySelector('.window.open');
    if (windowActive) {
      windowClose(windowActive, false);
    } else {
      bodyLock();
    }

    for(let i = 0; i < arrayScrVideo.length;i++) {
      if(currentWindow === arrayScrVideo[i][0]) {
        iframe = getIframe(currentWindow);
        if(iframe) {
          iframe.src = arrayScrVideo[i][1];
          arrayScrVideo.splice(i,1);
          break;
        }
      }
    }

    currentWindow.classList.add('open');
    currentWindow.addEventListener('click', function (e) {
      if (!e.target.closest('.window-content')) {
        windowClose(e.target.closest('.window'));
      }
    });
  }
}

function windowClose(windowActive, doUnlock = true) {
  if (unlock) {
    iframe = getIframe(windowActive);
    if(iframe) {
      var arr = [ windowActive, iframe.src];
      arrayScrVideo.push(arr);
      iframe.src = '';
    }
    windowActive.classList.remove('open');
    if (doUnlock) {
      bodyUnlock();
    }
  }
}

function getIframe(windowActive) {
  var trailerVideo = windowActive.getElementsByClassName('window-trailer')[0];
    if(trailerVideo) {
      var iframeList = trailerVideo.getElementsByTagName('iframe');
      if(iframeList.length > 0) {
        return iframeList[0];
      }
    }
    return null;
}

function bodyLock() {
  //const lockPaddingValue = window.innerWidth - document.querySelector('.container').offsetWidth + 'px';
  const lockPaddingValue = window.innerWidth - document.documentElement.clientWidth + 'px';

  if (lockPadding.length > 0) {
  for (let index = 0; index < lockPadding.length; index++) {
    const el = lockPadding[index];
    el.style.paddingRight = lockPaddingValue;
  }
}
  body.style.paddingRight = lockPaddingValue;
  body.classList.add('lock');
  unlock = false;
  setTimeout(function () {
    unlock = true;
  }, timeout);
}

function bodyUnlock() {
  setTimeout(function () {
    for (let index = 0; index < lockPadding.length; index++) {
      const el = lockPadding[index];
      el.style.paddingRight = '0px';
    }
    body.style.paddingRight = '0px';
    body.classList.remove('lock');
  }, timeout);

  unlock = false;
  setTimeout(function () {
    unlock = true;
  }, timeout);
}

document.addEventListener('keydown', function (e) {
  if (e.which === 27) {
    const windowActive = document.querySelector('.window.open');
    windowClose(windowActive);
  }
});

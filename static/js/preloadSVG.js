function drawStuff(c) {
  var t = new Date().getTime()
  for (var i = 0; i < 20; i++) {
    var s = Math.sin(t / 1000 + i * 0.8)
    var cs = Math.cos(t / 1000 + i * 0.8)
    var y = -i * 10 + 150 - 20 * s
    c.beginPath()
    var lw = (5 - Math.abs(i - 5) + 1)
    c.lineWidth = lw
    x = 100 + cs * 20 - 0.75 * (5 - Math.abs(i - 5) + 1)
    c.moveTo(x + lw * 0.5, y)
    c.lineTo(x + lw * 0.5, y + 8 * (5 - Math.abs(i - 5) + 1))
    c.stroke()
  }
}

function noCrash() {
  var w = document.body.clientWidth
  var h = document.body.clientHeight
  var t = new Date().getTime()
  var c = rebootLoad.ctx
  c.save()
  c.lineCap = "round"
  c.clearRect(0, 0, 200, 200)
  drawStuff(c)
  c.restore()
}

function clear() {
  rebootLoad.ctx.clearRect(0, 0, 100, 100)
}
var e = document.getElementById("rebootLoad")
rebootLoad = e
rebootLoad.ctx = e.getContext("2d")
e.style.left = document.body.clientWidth / 2 - 100
e.style.top = document.body.clientHeight / 2 - 100
setInterval(noCrash, 33)
window.onresize = function(ev) {
  e.style.left = document.body.clientWidth / 2 - 100
  e.style.top = document.body.clientHeight / 2 - 100
  noCrash()
}
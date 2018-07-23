<template>
  <div class="po-hello">
    <div class="container-fluid">
      <div class="row">
        <div class="col-md-12 jumbotron">
          <h2>
            <span class="potato-brand-text">
              Potato OJ
            </span>, 不仅仅是刷题!
          </h2>
          <p>在这里，你可以：</p>
          <div class="row">
            <div class="col-md-4 feature-box">
              <div class="feature-list-box">
                <ul>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">Python3.4</div>
                    <div class="col-md-6 language-cell-yes">Python2.7</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">Java 8</div>
                    <div class="col-md-6 language-cell-yes">C++11</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">GCC</div>
                    <div class="col-md-6 language-cell-no">Go*</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-no">JavaScript ES6*</div>
                    <div class="col-md-6 language-cell-no">Haskell*</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-no">Ruby*</div>
                    <div class="col-md-6 language-cell"></div>
                  </li>
                </ul>
              </div>
            </div>
            <div class="col-md-4 feature-box">
              <div class="feature-code-box">
                <textarea id="code-editor-example">{{ code_example }}</textarea>
              </div>
            </div>
            <div class="col-md-4 feature-box">
              <div class="feature-list-box">
                <ul>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">动态规划</div>
                    <div class="col-md-6 language-cell-yes">线段树</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">贪心</div>
                    <div class="col-md-6 language-cell-yes">舞蹈链</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">分治</div>
                    <div class="col-md-6 language-cell-yes">树状数组</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">搜索</div>
                    <div class="col-md-6 language-cell-yes">概率论</div>
                  </li>
                  <li class="row">
                    <div class="col-md-6 language-cell-yes">图论</div>
                    <div class="col-md-6 language-cell-yes">数论</div>
                  </li>
                </ul>
              </div>    
            </div>
          </div>
          <div class="row feature-text-box">
            <div class="col-md-4 feature-text">
              <p>使用你喜欢的语言</p>
            </div>
            <div class="col-md-4 feature-text">
              <p>使用易用的在线编辑器</p>
            </div>
            <div class="col-md-4 feature-text">
              <p>解决有趣的编程挑战</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var NProgress = window.NProgress
export default {
  name: 'Hello',
  data () {
    return {
      code_example: '//Vim, Emacs and Sublime Text3 mode\n#include <iostream>\nusing namespace std;\n\nint main(void){\n  int a, b;\n  while(cin >> a >> b)\n    cout << a + b << endl;\n  return 0;\n}'
    }
  },
  route: {
    waitForData: true,
    // input params in here, default NaN
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      NProgress.done()
      transition.next({})
    }
  },
  methods: {},
  ready: function () {
    // Code Mirror
    let self = this
    require([
      'codemirror',
      'codemirror/mode/clike/clike.js'
    ], function (CodeMirror) {
      self.code_editor = CodeMirror.fromTextArea(document.getElementById('code-editor-example'), {
        lineNumbers: true,
        mode: 'text/x-c++src',
        theme: 'neo',
        indentUnit: 2,
        tabSize: 2,
        showCursorWhenSelecting: true,
        matchBrackets: true
      })
    })
  },
  components: {}
}
</script>

<style lang='less'>
.po-hello {
  .container-fluid {
    padding-left: 0px;
    padding-right: 0px;
  }

  .jumbotron {
    background-color: rgba(0, 128, 0, 0.03);
    border-radius: 0px;
    padding-bottom: 25px;
  }

  .potato-brand-text {
    font-family: 'Audiowide', cursive;
    color: #E75440;
  }

  .feature-box {

    .feature-list-box {
      height: 260px;
      background-color: white;
      text-align: left;
      font-family: Consolas, Courier New;
      font-size: 16px;

      padding-top: 50px;

      li {
        list-style-type: none;

        margin-left: 0px;
        margin-right: 0px;
        margin-bottom: 10px;

        .language-cell-yes {
          border-left-width: 3px;
          border-left-color: green;
          border-left-style: solid;
        }

        .language-cell-no {
          border-left-width: 3px;
          border-left-color: #E75440;
          border-left-style: solid;
        }
      }
    }

    .feature-code-box {
      height: 260px;
      background-color: white;
    }

    .feature-player-box {
      height: 260px;
      background-color: white;
    }
  }

  .feature-text-box {
    margin-top: 25px;
    .feature-text {
      p {
        font-size: 18px;
        font-weight: 500;
      }
      text-align: center;
    }
  }
}
</style>

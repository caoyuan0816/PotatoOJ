<template>
  <div class="po-problem-details">
    <div class="container-fuild">
      <div class="row">
        <div class="col-md-7 problem-details-content" id="problem-content">
          <h2>{{ problem.title }}</h2>
          <div class="problem-details-header">
            <p>Time: {{ problem.time_limit }} ms</p>
            <p>Memory: {{ problem.memory_limit }} KB</p>
            <p>Update Date: {{ problem.modify_date}}</p>
          </div>
          <p>{{{ problem.description }}}</p>
          <h3>Input</h3>
          <p>{{{ problem.description_input }}}</p>
          <h3>Output</h3>
          <p>{{{ problem.description_output }}}</p>
          <h3>Sample Input</h3>
          <pre>{{{ problem.sample_input }}}</pre>
          <h3>Sample Output</h3>
          <pre>{{{ problem.sample_output }}}</pre>
          <h3 v-if="problem.hint">Hint</h3>
          <p>{{{ problem.hint }}}</p>
        </div>
        <div class="col-md-5 problem-details-submit" id="problem-submit">
          <textarea id="code-editor">{{ code_editor_data.value }}</textarea>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12 problem-details-controller">
          <button class="btn btn-success" id="button-submit" @click="submit">Submit</button>
          <button class="btn btn-warning" @click="save">Save</button>
          <div class="dropup problem-details-controller-select">
            Editor Mode: 
            <v-select 
               placeholder="Editor Mode"
               :options="get_editor_mode_options"
               :value.sync="code_editor_data.mode"
               :close-on-select="true">
            </v-select>
          </div>
          <div
              class="dropup problem-details-controller-select"
              id="controller-lang">
            Language: 
            <v-select
               placeholder="Language"
               :options="get_editor_lang_options"
               :value.sync="code_editor_data.lang"
               :close-on-select="true">
            </v-select>
          </div>
        </div>
      </div>
    </div>
    <alert 
      type="warning"
      :show.sync="showAlert"
      :duration="3000"
      width="400px"
      placement="top-right"
      dismissable>
      <strong>Warning!</strong>
      <p>You need to login before you submit code.</p>
    </alert>
    <alert 
      type="success"
      :show.sync="showSuccess"
      width="400px"
      placement="top-right"
      dismissable>
      <strong>Submit Success!</strong>
      <p>Go to <a v-link="{ path: '/statuslist' }">status page</a>.</p>
    </alert>
  </div>
</template>

<script>
import { select } from 'vue-strap'
import { option } from 'vue-strap'
import { alert } from 'vue-strap'
var NProgress = window.NProgress
var Markdown = require('markdown').markdown
var Cookie = window.Cookie
export default {
  name: 'ProblemDetails',
  data () {
    return {
      problem: {},
      code_editor: null,
      code_editor_data: {
        value: '#include <iostream>\nusing namespace std;\n\nint main(void){\n  int a, b;\n  while(cin >> a >> b)\n    cout << a + b << endl;\n  return 0;\n}\n',
        lang: '2',
        mode: '1',
        lang_config: {
          'C': 'text/x-csrc',
          'C++': 'text/x-c++src',
          'Java': 'text/x-java',
          'Python2': 'text/x-python',
          'Python3': 'text/x-python'
        },
        keymap_config: {
          'Sublime Text': 'sublime',
          'Vim': 'vim',
          'Emacs': 'emacs'
        }
      },
      language_code_list: [
        'C',
        'C++',
        'Java',
        'Python2',
        'Python3'
      ],
      keymap_code_list: [
        'Sublime Text',
        'Vim',
        'Emacs'
      ],
      theme: 'neo',
      showAlert: false,
      showSuccess: false
    }
  },
  computed: {
    get_editor_mode_options: function () {
      let editor_mode_options = []
      for (let i = 0; i < this.keymap_code_list.length; i++) {
        let dict = {}
        dict['value'] = i + 1 + ''
        dict['label'] = this.keymap_code_list[i]
        editor_mode_options.push(dict)
      }
      return editor_mode_options
    },
    get_editor_lang_options: function () {
      let editor_lang_options = []
      for (let i = 0; i < this.language_code_list.length; i++) {
        let dict = {}
        dict['value'] = i + 1 + ''
        dict['label'] = this.language_code_list[i]
        editor_lang_options.push(dict)
      }
      return editor_lang_options
    }
  },
  methods: {
    submit: function () {
      // Check user war logged in.
      // Anonymous user can not submit.
      if (!this.$root.$refs.navbar.isLogin) {
        this.showAlert = true
        return
      }
      // Disable submit button first
      document.getElementById('button-submit').className = 'btn btn-success disabled'
      NProgress.start()
      NProgress.set(0.6)

      let code = encodeURIComponent(this.code_editor.getValue())
      let language = parseInt(this.code_editor_data.lang) - 1
      let question = this.$route.params.pid
      let csrftoken = Cookie.get('csrftoken')
      let self = this

      window.fetch('/api/submit/', {
        method: 'post',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        credentials: 'include',
        body: encodeURI(`code=${code}&language=${language}&question=${question}&csrfmiddlewaretoken=${csrftoken}`)
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        console.log(data)
        self.showSuccess = true
        NProgress.done()
      }).catch(function (error) {
        console.log('Error happned submit', error)
        NProgress.done()
      })

      // Resume submit button
      document.getElementById('button-submit').className = 'btn btn-success'
    },
    save: function () {
      console.log('Saving')
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let pid = this.$route.params.pid
      window.fetch(`/api/question/${pid}/?format=json`, {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          transition.next({
            problem: {
              title: data.question.title,
              source: data.question.source,
              description: Markdown.toHTML(data.question.description),
              description_input: Markdown.toHTML(data.question.description_input),
              description_output: Markdown.toHTML(data.question.description_output),
              sample_input: Markdown.toHTML(data.question.sample_input),
              sample_output: Markdown.toHTML(data.question.sample_output),
              hint: Markdown.toHTML(data.question.hint),
              time_limit: data.question.time_limit,
              memory_limit: data.question.memory_limit,
              is_special_judge: data.question.is_special_judge,
              add_date: (/.{19}/).exec(data.question.add_date.replace(/T/, ' ')),
              modify_date: (/.{19}/).exec(data.question.modify_date.replace(/T/, ' '))
            }
          })
        } else {
          console.log('get question details failed')
          console.log(data.detail)
        }
      }).catch(function (error) {
        NProgress.done()
        console.log(`Error happend: /api/question/${pid} =>`, error)
      })
    }
  },
  ready: function () {
    // Set problem conteng height
    let current_window_height = (window.innerHeight - 84) + 'px'
    document.getElementById('problem-content').style.height = current_window_height
    document.getElementById('problem-submit').style.height = current_window_height

    let self = this
    // Init codemirror
    require([
      'codemirror',
      'codemirror/mode/clike/clike.js',
      'codemirror/mode/python/python.js',
      'codemirror/keymap/vim.js',
      'codemirror/keymap/emacs.js',
      'codemirror/keymap/sublime.js',
      'codemirror/addon/dialog/dialog.js'
    ], function (CodeMirror) {
      CodeMirror.commands.save = function () {
        self.save()
      }
      self.code_editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        lineNumbers: true,
        mode: self.code_editor_data.lang_config[self.language_code_list[self.code_editor_data.lang - 1]],
        keyMap: self.code_editor_data.keymap_config[self.keymap_code_list[self.code_editor_data.mode - 1]],
        theme: 'neo',
        indentUnit: 2,
        tabSize: 2,
        showCursorWhenSelecting: true,
        matchBrackets: true
      })
      /*
      self.code_editor.on('vim-keypress', function (key) {
        console.log(key)
      })
      */
      document.getElementsByClassName('CodeMirror')[0].style.height = current_window_height

      // Register events watching
      // mode setting watcher
      self.$watch('code_editor_data.lang', function (val) {
        let MIME = self.code_editor_data.lang_config[self.language_code_list[val - 1]]
        self.code_editor.setOption('mode', MIME)
      })

      // keymap setting watcher
      self.$watch('code_editor_data.mode', function (val) {
        let keymap_mode = self.code_editor_data.keymap_config[self.keymap_code_list[val - 1]]
        self.code_editor.setOption('keyMap', keymap_mode)
      })

      NProgress.done()
    })
  },
  components: {
    'v-select': select,
    'v-option': option,
    'alert': alert
  }
}
</script>

<style lang='less'>
@header-border-color: green;
@code-border-color: #E75440;

@head-font: Consolas, Courier New;
@content-font: Consolas, Courier New;
@content-size: 16px;
@code-font: Consolas, Courier New;

.po-problem-details {
  .row {
    margin-left: 0px;
    margin-right: 0px;
  }
  .problem-details-content{
    overflow-y: scroll;
    overflow-x: hidden;

    .problem-details-header {
      margin-top: 30px;
      margin-bottom: 30px;
      border-left-width: 3px;
      border-left-color: @header-border-color;
      border-left-style: solid;
      padding-left: 20px;
    }
    h3 {
      font-family:@head-font;
    }
    p {
      font-size: @content-size;
      font-family: @content-font;
      font-weight: 400;
    }
    pre {
      padding: 0px 0px 0px 10px;
      border-left-width: none;
      background-color: white;
      border-radius: 0px;
      border: 0px none white;
      border-left-width: 3px;
      border-left-style: solid;
      border-left-color: @code-border-color;
    }
    pre p{
      font-family: @code-font;
      font-size: @content-size;
      background-color: white;
      margin-bottom: 0px;
    }
  }

  .problem-details-submit {
    /*background-color: black;*/
    padding-left: 0px;
    padding-right: 0px;

    #code-editor {
      visibility: hidden;
    }
  }

  .problem-details-controller {
    background-color: rgba(93, 164, 195, 0.06);
    padding-top: 3px;
    padding-bottom: 3px;

    border-top-color: #e7e7e7;
    border-top-width: 1px;
    border-top-style: solid;

    button {
      font-family: Consolas, Courier New;
      margin-left: 15px;
      float: right;
      border-radius: 2px;
      line-height: 12px;
    }

    .problem-details-controller-select {
      margin-left: 15px;
      float: right;
      font-family: Consolas, Courier New;

      ul {
        font-family: Consolas, Courier New;
      }
    }
  }
}
</style>

<template>
  <div class="po-contest-details">
    <div class="container-fuild">
      <div class="row">
        <div class="col-md-7" id="problem-box">
          <div id="contest-title">
            <h1>{{ contest.title }}
              <span style="font-size: 16px;">
                <span class="label label-success btn-xs" v-if="is_running">Running</span>
                <span class="label label-danger btn-xs" v-if="is_finished">Finished</span>
                <span class="label label-info btn-xs" v-if="!is_finished && !is_running">Created</span>
                <button 
                  class="btn btn-success btn-sm btn-rank-list"
                  v-link="{ path: '/contest/' + contest.id + '/ranklist'}">Rank</button>
              </span>
            </h1>
            <div class="progressbar-text">
              Passed: {{ contest_running_time.hour }}:{{ contest_running_time.min }}:{{ contest_running_time.sec }}
            </div>
            <div id="progressbar-container"></div>
            <div class="progressbar-text" style="padding-bottom: 20px;">
              <span style="float:right;">Length: {{ contest.contest_len.hour }}:{{ contest.contest_len.min }}:{{ contest.contest_len.sec }}</span>
            </div>
            <!--<p>Current rank: #1</p>-->
          </div>
          <tabs v-ref:tabs>
              <tab 
                  v-for="pub_question in contest.pub_questions_details"
                  :header="get_tab_title(pub_question.question_serial_letter)">
                <div class="col-md-12 problem-details-content">
                  <h2>{{ pub_question.question_detail.title }}</h2>
                  <div class="problem-details-header">
                    <p>Time: {{ pub_question.question_detail.time_limit }} ms</p>
                    <p>Memory: {{ pub_question.question_detail.memory_limit }} KB</p>
                    <p>Update Date: {{ pub_question.question_detail.modify_date.toLocaleDateString() }}</p>
                  </div>
                  <p>{{{ pub_question.question_detail.description }}}</p>
                  <h3>Input</h3>
                  <p>{{{ pub_question.question_detail.description_input }}}</p>
                  <h3>Output</h3>
                  <p>{{{ pub_question.question_detail.description_output }}}</p>
                  <h3>Sample Input</h3>
                  <pre>{{{ pub_question.question_detail.sample_input }}}</pre>
                  <h3>Sample Output</h3>
                  <pre>{{{ pub_question.question_detail.sample_output }}}</pre>
                  <h3 v-if="pub_question.question_detail.hint">Hint</h3>
                  <p>{{{ pub_question.question_detail.hint }}}</p>
                </div>
              </tab>
          </tabs>
        </div>
        <div class="col-md-5 problem-details-submit" id="problem-submit">
          <textarea id="code-editor">{{ code_editor_data.value }}</textarea>
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
    </div>
    <alert 
      type="success"
      :show.sync="showSuccess"
      width="400px"
      :duration="3000"
      placement="top-right"
      dismissable>
      <strong>Submit Success!</strong>
      <p>Go to <a v-link="{ path: '/statuslist' }">status page</a>.</p>
    </alert>
    <alert 
      type="danger"
      :show.sync="showFailed"
      width="400px"
      :duration="3000"
      placement="top-right"
      dismissable>
      <strong>Submit Failed!</strong>
      <p>Contest is over!</p>
    </alert>
  </div>
</template>

<script>
// import { tabset } from 'vue-strap'
// import { tab } from 'vue-strap'
import { select } from 'vue-strap'
import { option } from 'vue-strap'
import { alert } from 'vue-strap'
var NProgress = window.NProgress
var Markdown = require('markdown').markdown
var Progressbar = require('progressbar.js')
var Cookie = window.Cookie
export default {
  name: 'ContestDetails',
  data () {
    return {
      contest: {
        contest_len: {
          NaN
        }
      },
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
      contest_running_time: {
        raw: NaN,
        hour: '-',
        min: '--',
        sec: '--'
      },
      is_running: false,
      is_finished: false,
      progress: 0,
      update_interval: NaN,
      current_active_tab: 0,
      showSuccess: false,
      showFailed: false
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
    save: function () {
      console.log('Saving')
    },
    submit: function () {
      // Check contest is or not running
      if (!this.is_running) {
        this.showFailed = true
        return
      }
      // Disable submit button first
      document.getElementById('button-submit').className = 'btn btn-success disabled'
      NProgress.start()
      NProgress.set(0.6)

      let code = encodeURIComponent(this.code_editor.getValue())
      let language = parseInt(this.code_editor_data.lang) - 1
      let question = this.contest.pub_questions_details[this.current_active_tab].question_detail.id
      let csrftoken = Cookie.get('csrftoken')
      let contest = this.contest.id
      let self = this

      window.fetch('/api/submit/', {
        method: 'post',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        credentials: 'include',
        body: encodeURI(`code=${code}&language=${language}&question=${question}&contest=${contest}&csrfmiddlewaretoken=${csrftoken}`)
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
    update_contest_running_time: function () {
      // Check contest is running
      let current_time = Date.now()
      let start_time = this.contest.start_time.getTime()
      let running_time = (current_time - start_time) / 1000
      if (running_time >= 0) {
        if (running_time >= this.contest.contest_len.raw) {
          this.is_finished = true
          this.contest_running_time = {
            raw: NaN,
            hour: this.contest.contest_len.hour,
            min: this.contest.contest_len.min,
            sec: this.contest.contest_len.sec
          }
          this.progress = 1
        } else {
          this.is_running = true
          let raw = running_time
          let hour = parseInt(running_time / 3600)
          running_time = running_time - hour * 3600
          let min = parseInt(running_time / 60)
          running_time = running_time - min * 60
          if (min < 10) {
            min = '0' + min
          }
          let sec = parseInt(running_time)
          if (sec < 10) {
            sec = '0' + sec
          }
          // Set running_time
          this.contest_running_time = {
            raw: raw,
            hour: hour,
            min: min,
            sec: sec
          }
          // Calculate and set progress bar value
          let progress_value = raw / this.contest.contest_len.raw
          this.progress = progress_value
        }
      } else {
        this.contest_running_time = {
          raw: NaN,
          hour: '-',
          min: '--',
          sec: '--'
        }
      }
    },
    get_tab_title: function (data) {
      return `<span class="tab-title-order">${data}</span><span class="tab-title-number"> 0/10 </span>`
    },
    trim_data: function (data) {
      data.contest.start_time = new Date(data.contest.start_time)
      data.contest.finish_time = new Date(data.contest.finish_time)
      // Calculate contest length
      let contest_len = (data.contest.finish_time - data.contest.start_time) / 1000
      data.contest.contest_len = {}
      data.contest.contest_len.raw = contest_len
      data.contest.contest_len.hour = parseInt(contest_len / 3600)
      contest_len = contest_len - data.contest.contest_len.hour * 3600
      data.contest.contest_len.min = parseInt(contest_len / 60)
      if (data.contest.contest_len.min < 10) {
        data.contest.contest_len.min = '0' + data.contest.contest_len.min
      }
      contest_len = contest_len - data.contest.contest_len.min * 60
      data.contest.contest_len.sec = contest_len
      if (data.contest.contest_len.sec < 10) {
        data.contest.contest_len.sec = '0' + data.contest.contest_len.sec
      }
      data.contest.pub_questions_details = data.contest.pub_questions_details.map(function (n) {
        n.question_detail.description = Markdown.toHTML(n.question_detail.description)
        n.question_detail.description_input = Markdown.toHTML(n.question_detail.description_input)
        n.question_detail.description_output = Markdown.toHTML(n.question_detail.description_output)
        n.question_detail.sample_input = Markdown.toHTML(n.question_detail.sample_input)
        n.question_detail.sample_output = Markdown.toHTML(n.question_detail.sample_output)
        n.question_detail.hint = Markdown.toHTML(n.question_detail.hint)
        n.question_detail.add_date = new Date(n.question_detail.add_date)
        n.question_detail.modify_date = new Date(n.question_detail.modify_date)
        return n
      })
      return data
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let cid = this.$route.params.cid
      let self = this
      window.fetch(`/api/contest/${cid}/?format=json`, {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          transition.next({
            contest: data.contest
          })
        }
      }).catch(function (error) {
        NProgress.done()
        console.log(`Error happned: /api/contest/${cid}/ =>`, error)
      })
    }
  },
  ready: function () {
    // Set problem conteng height
    let current_window_height = (window.innerHeight - 84) + 'px'
    document.getElementById('problem-submit').style.height = current_window_height
    // console.log(document.getElementsByClassName('problem-details-content'))
    let self = this
    // Init codemirror
    require([
      'codemirror',
      'codemirror/mode/clike/clike.js',
      'codemirror/mode/python/python.js',
      'codemirror/keymap/vim.js',
      'codemirror/keymap/emacs.js',
      'codemirror/keymap/sublime.js',
      'codemirror/addon/dialog/dialog.js',
      'codemirror/addon/hint/show-hint.js',
      'codemirror/addon/search/search.js'
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
      document.getElementsByClassName('CodeMirror')[0].style.height = current_window_height
      // Progress bar
      let line = new Progressbar.Line('#progressbar-container', {
        // color: '#E75440',
        color: '#409300',
        // trailColor: '#DDF0ED',
        trailColor: 'white',
        duration: 1000,
        trailWidth: 1,
        svgStyle: {
          height: '3px',
          width: '100%',
          display: 'block'
        }
      })
      // Set progress bar watching
      self.$watch('progress', function (val) {
        // console.log(val)
        line.animate(val)
      })
      // Set update time interval
      if (isNaN(self.update_interval)) {
        self.update_interval = setInterval(self.update_contest_running_time.bind(self), 500)
      }
      self.$nextTick(function () {
        let question_contents = document.getElementsByClassName('problem-details-content')
        let problem_content_height = (window.innerHeight - 84 - 42 - 87 - 6) + 'px'
        for (let i = 0; i < question_contents.length; i++) {
          question_contents.item(i).style.height = problem_content_height
        }
      })
      NProgress.done()
    })
  },
  beforeDestroy: function () {
    clearInterval(this.update_interval)
    this.refresh_interval = NaN
  },
  components: {
    'tabs': require('../components/sub_components/Tabset.vue'),
    'tab': require('../components/sub_components/Tab.vue'),
    // 'tabs': tabset,
    // 'tab': tab,
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
.po-contest-details {
  .row {
    margin-left: 0px;
    margin-right: 0px;
  }

  #problem-box {
    padding-left: 0px;
    padding-right: 0px;
  }

  #contest-title {
    h1 {
      margin-top: 5px;
      margin-bottom: 5px;
    }
  }

  .nav-tabs {
    margin-bottom: 0px;
  }

  .problem-details-content {
    overflow-y: scroll;
    overflow-x: hidden;

    height: 100%;

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

  .progressbar-text {
    font-family: @content-font;
  }

  .nav-tabs {
    li {
      a {
        .tab-title-order {
          font-weight: bold;
        }
        .tab-title-number {
          font-family: @content-font;
        }
        padding-left: 5px;
        padding-right: 5px;
        /*font-family: @content-font;*/
      }
    }
  }

  .btn-rank-list {
    border-radius: 2px;
    line-height: 1;
  }
}
</style>

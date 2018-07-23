<template>
  <div class="po-status-details">
    <div class="container">
      <div class="row">
        <div class="col-md-12" id="status-details-content">
          <template v-if="success">
            <h2>Mission #{{ status.id }}</h2>
            <div class="status-title-green">
              <p>Result: <span v-bind:class="[get_status_color()]">{{ status_code_list[status.status] }}</span></p>
              <p>Question: <a v-link="{ path: '/problem/' + status.question_details.id}">{{ status.question_details.title }}</a></p>
              <p>User: <a v-link="{ path: '/user/' + status.user_details.id }">{{ status.user_details.username }}</a></p>
              <p>Language: {{ language_code_list[status.language] }}</p>
              <p>Submit Time: {{ status.submit_time }}</p>
              <p>Judge Time: {{ status.judge_time }}</p>
            </div>
            <template v-if="parseInt(status.status) === 4">
              <div class="status-title-green">
                <p>Memory: {{ status.mem }} KB</p>
                <p>Time: {{ status.time }} ms</p>
              </div>
            </template>
            <template v-else>
              <div class="status-title-red">
                <p>{{ status.judge_info }}</p>
              </div>
            </template>
            <div class="status-code">
              <pre>
                <code id="status-details-code">
{{ status.code }}
                </code>
              </pre> 
            </div>
          </template>
          <template v-else>
            <div class="status-title-red">
              {{ message }}
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var NProgress = window.NProgress
var hljs = require('highlight.js')
export default {
  name: 'StatusDetails',
  data () {
    return {
      status: {
        question_details: {},
        user_details: {}
      },
      success: true,
      status_code_list: [
        'Waiting',
        'Judging',
        'Compiling',
        'Running',
        'Accepted',
        'CompileError',
        'WrongAnswer',
        'RuntimeError',
        'TimeLimitExceeded',
        'MemoryLimitExceeded',
        'OutputLimitExceeded',
        'PresentationError',
        'SystemError'
      ],
      language_code_list: [
        'C',
        'C++',
        'Java',
        'Python2',
        'Python3'
      ]
    }
  },
  methods: {
    trim_data: function (data) {
      data.status.submit_time = new Date(data.status.submit_time).toLocaleString()
      data.status.judge_time = new Date(data.status.judge_time).toLocaleString()
      if (data.status.status === '4') {
        let judge_info_data = data.status.judge_info.split(/,/)
        if (judge_info_data[0].match(/time/) === null) {
          data.status.mem = parseInt(judge_info_data[0].match(/\d+.\d+/))
          data.status.time = parseInt(judge_info_data[1].match(/\d+.\d+/))
        } else {
          data.status.time = parseInt(judge_info_data[0].match(/\d+.\d+/))
          data.status.mem = parseInt(judge_info_data[1].match(/\d+.\d+/))
        }
      }
      return data
    },
    get_status_color: function (data) {
      if (parseInt(this.status.status) === 4) {
        return 'text-green'
      } else {
        return 'text-red'
      }
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let self = this
      let sid = this.$route.params.sid
      window.fetch(`/api/status/${sid}`, {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          transition.next({
            status: data.status
          })
        } else {
          transition.next({
            success: false,
            message: data.detail
          })
        }
        NProgress.done()
      }).catch(function (error) {
        NProgress.done()
        console.log(`Error happend: /api/status/${sid} =>`, error)
      })
    }
  },
  ready: function () {
    this.$nextTick(function () {
      let code_area = document.getElementById('status-details-code')
      hljs.highlightBlock(code_area)
    })
  }
}
</script>

<style lang='less'>
@potato-color: #E75440;
@content-font: Consolas, Courier New;
.po-status-details {
  .status-title-green {
    margin-top: 30px;
    margin-bottom: 30px;
    border-left-width: 3px;
    border-left-color: green;
    border-left-style: solid;
    padding-left: 20px;
    font-family: @content-font;
    font-size: 16px;
  }

  .status-title-red {
    margin-top: 30px;
    margin-bottom: 30px;
    border-left-width: 3px;
    border-left-color: @potato-color;
    border-left-style: solid;
    padding-left: 20px;
    font-family: @content-font;
    font-size: 16px;
  }

  .text-green {
    color: green;
  }

  .text-red {
    color: red;
  }
  pre {
    border-style: none;
    border-radius: 0px;
    padding: 0px 0px 0px 0px;
    margin: 0px 0px 0px 0px;
    background-color: white;
    font-size: 16px;
  }
  pre code {
    background-color: white;
    border-left-width: 3px;
    border-left-color: rgb(40, 154, 216);;
    border-left-style: solid;
    padding: 0px 0px 0px 0px;
    margin: 0px 0px 0px 0px;
    padding-left: 20px;
    margin-top: -20px;
  }
}

</style>

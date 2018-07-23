<template>
  <div class="po-status-list">
    <div class="container">
      <ul>
        <template v-for="status in statuses">
          <li class="row">
            <div class="col-md-5"
                 v-bind:class="[parseInt(status.status) === 4 ? borderGreen : parseInt(status.status) <= 3 ? borderOther : borderRed]">
              <span v-bind:class="[parseInt(status.status) === 4 ? contentGreen : parseInt(status.status) <= 3 ? contentOther : contentRed]">
                {{ status_code_list[status.status] }}
              </span>
              <br/>
              <span class="sub-title">
                  #{{ status.id }} - {{ status.question_details.title }} - {{ status.submit_time }}
              </span>
            </div>
            <div class="col-md-2 status-statistic">
              <a v-link="{ path: '/user/' + status.user_details.id }">
                {{ status.user_details.username }}
              </a>
              <br/>
              <span class="sub-title">
                User
              </span>
            </div>
            <div class="col-md-1 status-statistic">
              <template v-if="parseInt($root.$refs.navbar.current_user_id) === parseInt(status.user_details.id)">
                <a v-link="{ path: '/status/' + status.id}">
                  {{ language_code_list[parseInt(status.language)] }}
                </a>
              </template>
              <template v-else>
                {{ language_code_list[parseInt(status.language)] }}
              </template>
              <br/>
              <span class="sub-title">
                Language
              </span>
            </div>
            <div class="col-md-1 status-statistic">
              {{ status.time }}
              <br/>
              <span class="sub-title">
                Time (ms)
              </span>
            </div>
            <div class="col-md-1 status-statistic">
              {{ status.mem }}
              <br/>
              <span class="sub-title">
                Mem (KB)
              </span>
            </div>
            <div class="running-spinner col-md-1">
              <div class="running-icon"
                   v-show="parseInt(status.status) <= 3">
              </div> 
            </div>
          </li>
        </template>
      </ul>
    </div>
  </div>
</template>

<script>
var NProgress = window.NProgress
export default {
  name: 'StatusList',
  data () {
    return {
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
      ],
      statuses: [
        // currently format:
        // {id: 1, problem: 2, status: 'Accepted'}
      ],
      borderRed: 'border-red',
      borderGreen: 'border-green',
      borderOther: 'border-other',
      contentRed: 'content-red',
      contentGreen: 'content-green',
      contentOther: 'content-other',
      refresh_interval: null
    }
  },
  methods: {
    refresh_data: function () {
      NProgress.start()
      NProgress.set(0.6)
      let self = this
      window.fetch('/api/status/?format=json', {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          self.statuses = data.statuses
        } else {
          console.log('get status data failed')
          console.log(data.detail)
        }
        NProgress.done()
      }).catch(function (error) {
        NProgress.done()
        console.log('Error happend: /api/status/ =>', error)
      })
    },
    trim_data: function (data) {
      for (let i = 0; i < data.statuses.length; i++) {
        // Format time data
        data.statuses[i].submit_time = (/.{19}/).exec(data.statuses[i].submit_time.replace(/T/, ' '))

        // Set time and ,a
        if (data.statuses[i].status === '4') {
          let judge_info_data = data.statuses[i].judge_info.split(/,/)
          if (judge_info_data[0].match(/time/) === null) {
            data.statuses[i].mem = parseInt(judge_info_data[0].match(/\d+.\d+/))
            data.statuses[i].time = parseInt(judge_info_data[1].match(/\d+.\d+/))
          } else {
            data.statuses[i].time = parseInt(judge_info_data[0].match(/\d+.\d+/))
            data.statuses[i].mem = parseInt(judge_info_data[1].match(/\d+.\d+/))
          }
        } else {
          data.statuses[i].time = '-'
          data.statuses[i].mem = '-'
        }
      }
      return data
    }
  },
  ready: function () {
    if (this.refresh_interval === null) {
      this.refresh_interval = setInterval(this.$options.methods.refresh_data.bind(this), 5000)
    }
  },
  beforeDestroy: function () {
    clearInterval(this.refresh_interval)
    this.refresh_interval = null
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let self = this
      window.fetch('/api/status/?format=json', {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          transition.next({
            statuses: data.statuses
          })
        } else {
          console.log('get status data failed')
          console.log(data.detail)
        }
        NProgress.done()
      }).catch(function (error) {
        NProgress.done()
        console.log('Error happend: /api/status/ =>', error)
      })
    }
  }
}
</script>

<style lang='less'>

@content-padding:5px;
@border-width: 3px;
@link-color: #337ab7;
.po-status-list {
  ul {
    padding-left: 0px;
    padding-right: 0px;
  }

  li {
    list-style-type: none;
    font-size: 18px;
    padding-top: @content-padding;
    padding-bottom: @content-padding;

    a {
      line-height: 22px;
    }

    .border-red {
      border-left-width: @border-width;
      border-left-color: #E75440;
      border-left-style: solid;
    }

    .border-green {
      border-left-width: @border-width;
      border-left-color: green;
      border-left-style: solid;
    }

    .border-other {
      border-left-width: @border-width;
      border-left-color: rgb(40, 154, 216);
      border-left-style: solid;
    }

    .sub-title {
      font-size: 12px;
      line-height: 1px;
      color:#777;
    }

    .content-red {
      color: red;
    }

    .content-green {
      color: green;
    }

    .content-other {
      /*color: #46b8da;*/
      color: rgb(40, 154, 216);
    }

    .status-statistic {
      padding-top: 3px;
      font-size: 16px;
      text-align: center;
      color: @link-color;
    }

    .running-spinner {
    }

    .running-icon {
      width: 20px;
      height: 20px;
      box-sizing: border-box;
      margin-top: 15px;

      border: solid 2px transparent;
      border-top-color: #29d;
      border-left-color: #29d;
      border-radius: 50%;

      -webkit-animation: nprogress-spinner 400ms linear infinite;
              animation: nprogress-spinner 400ms linear infinite;
    }
  }
}
</style>

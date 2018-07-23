<template>
  <div class="po-contest-ranklist">
    <div class="container-fluid">
      <div class="row">
        <template v-if="success">
          <div class="col-md-8" id="problem-box">
            <div id="contest-title">
              <h1>{{ contest_rank.contest_details.title }}
                <span style="font-size: 16px;">
                  <span class="label label-success btn-xs" v-if="is_running">Running</span>
                  <span class="label label-danger btn-xs" v-if="is_finished">Finished</span>
                  <span class="label label-info btn-xs" v-if="!is_finished && !is_running">Created</span>
                  <button 
                    class="btn btn-success btn-sm btn-problem"
                    v-link="{ path: '/contest/' + contest_rank.contest_details.id }">Problems</button>
                </span>
              </h1> 
              <div class="progressbar-text">
                Passed: {{ contest_running_time.hour }}:{{ contest_running_time.min }}:{{ contest_running_time.sec }}
              </div>
              <div id="progressbar-container"></div>
              <div class="progressbar-text" style="padding-bottom: 20px;">
                <span style="float:right;">Length: {{ contest.contest_len.hour }}:{{ contest.contest_len.min }}:{{ contest.contest_len.sec }}</span>
              </div>
            </div>
            <div id="rank-table-box">
              <table class="table table-hover table-bordered rank-table">
                <thead>
                  <tr>
                    <th class="rank">
                      <span>#</span>
                    </th>
                    <th class="username">
                      <span>User</span>
                    </th>
                    <th class="solved">
                      <span style="color: green;">S</span>
                    </th>
                    <th class="penalty">
                      <span style="color: red;">P</span>
                    </th>
                    <th class="status" v-for="question_letter_single in contest_rank.question_letter_list">
                      <a herf="/">{{ question_letter_single }}</a>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rank in contest_rank.rank_list"
                      v-bind:class="[($index + 1) % 2 == 1 ? even : odd]">
                    <td>{{ $index + 1 }}</td>
                    <td class="rank-user">{{ rank.username }}</td>
                    <td>{{ rank.solved }}</td>
                    <td>{{ rank.total_time }}</td>
                    <td v-bind:class="[ get_table_cell_class(rank, contest_rank.question_letter_dict[question_letter_single]) ]"
                        v-for="question_letter_single in contest_rank.question_letter_list"
                        style="height:45px;">
                      <span v-if="status_is_ac(rank, contest_rank.question_letter_dict[question_letter_single])">
                        <span class="status-ac-punish">
                              +{{ rank[contest_rank.question_letter_dict[question_letter_single]].punish == 0 ? '' : rank[contest_rank.question_letter_dict[question_letter_single]].punish }}
                        </span>
                        <br/>
                        <span class="status-ac-time">
                              {{min_to_hour(rank[contest_rank.question_letter_dict[question_letter_single]].time - rank[contest_rank.question_letter_dict[question_letter_single]].punish * 20)}}
                        </span>
                      </span>
                      <span v-else>
                        <span v-if="status_exist(rank, contest_rank.question_letter_dict[question_letter_single])">-{{ rank[contest_rank.question_letter_dict[question_letter_single]].punish }}</span>
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="col-md-4" id="contest-status-box">
            <ul>
              <li class="row"
                  v-for="status in contest_status_list">
                <div class="col-sm-6 col-md-5 col-lg-4"
                     v-bind:class="[parseInt(status.status) === 4 ? borderGreen : parseInt(status.status) <= 3 ? borderOther : borderRed]">
                  <a v-bind:class="[parseInt(status.status) === 4 ? contentGreen : parseInt(status.status) <= 3 ? contentOther : contentRed]"
                     v-link="{ path: '/contest/' + contest_rank.contest_details.id + '/status/' + status.id }">
                    {{ status_code_list[status.status] }}
                  </a>
                </div>
                <div class="hidden-sm col-md-1 col-lg-1">
                  <a v-link="{ path: '/contest/' + contest_rank.contest_details.id + '/#q=' + contest_rank.question_letter_dict_reverse[status.question_details.id] }">{{ contest_rank.question_letter_dict_reverse[status.question_details.id] }}</a>
                </div>
                <div class="col-sm-6 col-md-5 col-lg-4" style="text-align: center;">
                  <a v-link="{ path: '/user/' + status.user_details.id }">{{ status.user_details.username }}</a>
                </div>
                <div class="hidden-sm hidden-md col-lg-3 contest-status-time">
                  {{ status.submit_time.replace('T', ' ').substring(10, 19) }}
                </div>
              </li>
            </ul>
          </div>
        </template>
        <template v-else>
          <p>{{ message }}</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
var NProgress = window.NProgress
var Progressbar = require('progressbar.js')
export default {
  name: 'ContestRankList',
  data () {
    return {
      success: true,
      contest_rank: {
        question_letter_list: [],
        contest_details: {}
      },
      contest: {
        contest_len: {}
      },
      contest_status_list: [],
      contest_running_time: {
        raw: NaN,
        hour: '-',
        min: '--',
        sec: '--'
      },
      even: 'even',
      odd: 'odd',
      status_ac_fb: 'status-ac-fb',
      status_ac: 'status-ac',
      status_not_ac: 'status-not-ac',
      is_running: false,
      is_finished: false,
      update_interval: NaN,
      progress: 0,
      borderRed: 'border-red',
      borderGreen: 'border-green',
      borderOther: 'border-other',
      contentRed: 'content-red',
      contentGreen: 'content-green',
      contentOther: 'content-other',
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
      ]
    }
  },
  methods: {
    status_exist: function (a, b) {
      if (b in a) {
        return true
      }
      return false
    },
    status_is_ac: function (a, b) {
      if (b in a) {
        if (a[b].ac === true) {
          return true
        }
      }
      return false
    },
    get_table_cell_class: function (a, b) {
      if (b in a) {
        if (a[b].ac === true) {
          if (a[b].fb === true) {
            return this.status_ac_fb
          }
          return this.status_ac
        }
        return this.status_not_ac
      }
      return null
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
    trim_data: function (data) {
      data.contest = {}
      data.contest.start_time = new Date(data.contest_rank.contest_details.start_time)
      data.contest.finish_time = new Date(data.contest_rank.contest_details.finish_time)
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
      return data
    },
    min_to_hour: function (data) {
      let hour = parseInt(data / 60)
      if (hour < 10) {
        hour = '0' + hour
      }
      let min = data % 60
      if (min < 10) {
        min = '0' + min
      }
      return '' + hour + ':' + min
    },
    update_status_data: function () {
      return {}
    },
    update_rank_data: function () {
      return {}
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let self = this
      let cid = this.$route.params.cid
      window.fetch(`/api/contest/ranklist/${cid}`, {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          let data_rank = self.trim_data(data)
          window.fetch(`/api/contest/statuslist/${cid}`, {
            credentials: 'include'
          }).then(function (response) {
            return response.json()
          }).then(function (data) {
            if (data.success) {
              let data_status = data
              transition.next({
                contest_rank: data_rank.contest_rank,
                contest: data_rank.contest,
                contest_status_list: data_status.contest_status_list
              })
            } else {
              transition.next({
                success: false,
                message: data.detail
              })
            }
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
        console.log(`Error happend: /api/contest/ranklist/${cid} =>`, error)
      })
    }
  },
  ready: function () {
    let self = this
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
    // Set table width
    let rank_table_box = document.getElementById('rank-table-box')
    let rank_width = (self.contest_rank.question_letter_list.length) * 80 + 140 + 240
    rank_table_box.style.width = rank_width + 'px'
    // rank_table_box.style.height = window.innerHeight - 50 - 42 - 43 + 'px'
    // Set contest status box height
    let contest_status_box = document.getElementById('contest-status-box')
    let contest_status_height = window.innerHeight - 50
    contest_status_box.style.height = contest_status_height + 'px'
  }
}
</script>

<style lang='less'>
@content-font: Consolas, Courier New;
@content-padding:5px;
@border-width: 3px;
.po-contest-ranklist {
  .container-fluid {
    padding-left: 0px;
    padding-right: 0px;
  }

  .row {
    margin-left: 0px;
    margin-right: 0px;
  }

  #rank-table-box {
    overflow-y: auto;
  }

  #problem-box {
    padding-left: 0px;
    padding-right: 0px;

    #contest-title {
      h1 {
        margin-top: 5px;
        margin-bottom: 5px;
      }
    }

    .btn-problem {
      border-radius: 2px;
      line-height: 1;
    }

    .progressbar-text {
      font-family: @content-font;
    }
  }

  #rank-table-box {
    padding-top: 15px;
    padding-left: 0px;
    padding-right: 0px;
    max-width: 100%;
  }

  th {
    background-color: white;
  }

  .rank {
    width: 40px;
  }

  .username {
  }

  .solved {
    width: 40px;
  }

  .penalty {
    width: 60px;
  }

  .status {
    width: 80px;
  }
  .rank-table tr th {
    text-align: center;
    border-bottom-width: 0px;
    vertical-align: middle;
    font-size: 14px;
    color: #555;
  }

  .rank-table tr td{
    text-align: center;
    vertical-align: middle;
    font-family: "微软雅黑","Helvetica Neue",Helvetica,Arial,sans-serif;
    line-height: 14px;
    padding-left: 0px;
    padding-right: 0px; 
  }

  .rank-user {
    font-weight: 700;
  }

  .even {
    background-color: rgb(248, 248, 248);
  }

  .odd {
    background-color: white;
  }
  
  .status-ac {
    background-color: rgb(212, 255, 208);
    vertical-align: middle;

    .status-ac-punish {
      font-size: 14px;
      color: #24A329;
    }

    .status-ac-time {
      font-size: 10px;
      color: #777;
    }
  }

  .status-ac-fb {
    background-color: #65bb81;
    vertical-align: middle;

    .status-ac-punish {
      font-size: 14px;
      color: white;
    }
    
    .status-ac-time {
      font-size: 10px;
      color: white;
    }
  }

  .status-not-ac {
    vertical-align: center;
    color: red;
    font-weight: 700;
    background-color: rgba(255, 0, 0, 0.1);
  }

  ul {
    padding-left: 0px;
    padding-right: 0px;
  }

  li {
    list-style-type: none;
    font-size: 16px;
    margin-top: 5px;
    margin-bottom: 7px;
    text-align: left;

    .contest-status-time {
      font-family: @content-font;
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
  } 

  #contest-status-box {
    overflow-y: scroll;
  }
}

</style>

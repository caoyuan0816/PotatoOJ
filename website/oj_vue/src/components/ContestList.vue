<template>
  <div class="po-contest-list">
    <div class="container">
      <ul>
        <template v-for="contest in contests">
          <li class="row">
            <div class="col-lg-4 col-md-5 col-sm-5"
                 v-bind:class="[borderRed]">
              <span>
                <a 
                  v-link="{ path: '/contest/' + contest.id }">
                  {{ contest.title }}
                </a>
              </span>
              <br/>
              <span class="sub-title">#{{ contest.id }} - {{ contest.create_time }}</span>
            </div>
            <div class="col-md-2 hidden-sm hidden-xs contest-statistic">
              <a>{{ contest.creater_details.username }}</a>
              <br/>
              <span class="sub-title">Manager</span>
            </div>
            <div class="col-md-1 hidden-sm hidden-xs contest-statistic">
              {{ contest.is_public ? 'public' : 'private' }}
              <br/>
              <span class="sub-title">Type</span>
            </div>
            <div class="col-lg-1 hidden-md hidden-sm hidden-xs contest-statistic">
              {{ '-' }}
              <br/>
              <span class="sub-title">Participant</span>
            </div>
            <div class="col-lg-4 col-md-4 hidden-sm hidden-xs contest-time">
              <span class="contest-time">{{ contest.start_time.toISOString().slice(0, 19).replace('T',' ') }} - {{ contest.finish_time.toISOString().slice(0, 19).replace('T',' ') }}</span>
              <br/>
              <span class="sub-title">
                <span class="label label-success btn-xs" v-if="contest.is_running">Running</span>
                <span class="label label-danger btn-xs" v-if="contest.is_finished">Finished</span>
                <span class="label label-info btn-xs" v-if="!contest.is_finished && !contest.is_running">Created</span>
              </span>
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
  name: 'ContestList',
  data () {
    return {
      contests: NaN,
        // Contest list
      borderRed: 'border-red',
      borderGreen: 'border-green'
    }
  },
  methods: {
    trim_data: function (data) {
      for (let i = 0; i < data.contests.length; i++) {
        // Format time data
        data.contests[i].create_time = new Date(data.contests[i].create_time)
        data.contests[i].start_time = new Date(data.contests[i].start_time)
        data.contests[i].finish_time = new Date(data.contests[i].finish_time)
        data.contests[i].is_running = false
        data.contests[i].is_finished = false
        let current_time = Date.now()
        if (data.contests[i].start_time <= current_time) {
          if (data.contests[i].finish_time < current_time) {
            data.contests[i].is_finished = true
          } else {
            data.contests[i].is_running = true
          }
        }
      }
      return data
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)

      let self = this
      window.fetch('/api/contests/?format=json', {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          transition.next({
            contests: data.contests
          })
        }
        NProgress.done()
      }).catch(function (error) {
        NProgress.done()
        console.log('Error happned: /api/contests/ =>', error)
      })
    }
  }
}
</script>

<style lang='less'>

@content-padding:5px;
@border-width: 3px;
.po-contest-list {
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

    .sub-title {
      font-size: 12px;
      line-height: 1px;
      color:#777;
    }

    .contest-statistic {
      padding-top: 3px;
      font-size: 16px;
      text-align: center;
    }

    .contest-time {
      padding-top: 3px;
      font-size: 16px;
    }
  }
}
</style>

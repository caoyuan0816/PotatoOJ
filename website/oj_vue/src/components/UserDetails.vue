<template>
  <div class='po-userdetails'>
    <div class='container'>
      <div class='row'>
        <div class='col-md-6'>
          <h1>
            {{ user.username }}
            <span class='user-details-label' v-if='user.is_staff'>Staff <span class='glyphicon glyphicon-ok'></span></span>
          </h1>
          <hr/>
          <h3>{{ user.profile.signature }}</h3>
          <hr/>
          <div class='user-details-bordered'>
            <p>Register time: {{ user.date_joined }}</p>
            <p>Last login: {{ user.last_login }}</p>
          </div>
          <hr/>
          <div class='user-details-bordered'>
            <p>Groups: <span v-for='group in user.groups'>{{ group }}</span></p>
          </div>
          <hr/>
        </div>
        <div class='col-md-6'>
          <canvas id='chart-submit-status' width='1000' height='500'></canvas>
        </div>
      </div>
      <div class='row'>
        <div class='col-md-12' id='chart-problem-status'>
          Problem status: 
          <hr/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var NProgress = window.NProgress
var d3 = require('d3')
var Chart = require('chart.js')
export default {
  name: 'UserDetails',
  data () {
    return {
      user: {
        profile: {}
      },
      is_me: false,
      chart_submit_status: null
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let self = this
      let uid = this.$route.params.uid
      window.fetch(`/api/user/${uid}/?format=json`, {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          transition.next({
            user: data.userdetails,
            is_me: data.is_me
          })
        }
      }).catch(function (error) {
        NProgress.done()
        console.log(`Error happned: /api/user/${uid}/ =>`, error)
      })
    }
  },
  methods: {
    trim_data: function (data) {
      data.userdetails.last_login = new Date(data.userdetails.last_login).toDateString()
      data.userdetails.date_joined = new Date(data.userdetails.date_joined).toDateString()
      return data
    }
  },
  ready: function () {
    let self = this
    // Draw submit status chart
    Chart.defaults.global.defaultFontFamily = 'Consolas, Courier New'
    Chart.defaults.global.defaultFontSize = 14
    Chart.defaults.global.animation.duration = 3000
    let ctx_chart_submit_status = document.getElementById('chart-submit-status')
    this.char_submit_status = new Chart(ctx_chart_submit_status, {
      type: 'bar',
      data: {
        labels: ['AC', 'CE', 'WA', 'RE', 'TLE', 'MLE', 'OLE', 'PE', 'SE'],
        datasets: [{
          label: self.user.username,
          backgroundColor: 'rgba(231, 84, 64, 0.6)',
          borderColor: 'rgba(255,99,132,1)',
          borderWidth: 0,
          hoverBackgroundColor: 'rgba(231, 84, 64, 0.8)',
          hoverBorderColor: 'rgba(231, 84, 64, 0.8)',
          data: self.user.profile.submitions
        }]
      },
      options: {
        scales: {
          xAxes: [{
            stacked: true,
            categoryPercentage: 0.9,
            gridLines: {
              display: false,
              color: 'black'
            }
          }],
          yAxes: [{
            display: false
          }]
        }
      }
    })

    // Draw problem status chart
    let svg_problem_status = d3.select('#chart-problem-status')
                               .append('svg')
                               .attr('preserveAspectRatio', 'xMinYMin meet')
                               .attr('viewBox', '0 0 1000 30')
                               .classed('svg-chart-problem-status', true)
    svg_problem_status.selectAll('rect')
                      .data(d3.range(1, 123))
                      .enter()
                      .append('rect')
                      .on('click', function (d, i) {
                        self.$router.go(`/problem/${d}`)
                      })
                      .on('mouseover', function (d, i) {
                        d3.select(this)
                          .attr('width', 10)
                          .attr('height', 10)
                      })
                      .on('mouseout', function (d, i) {
                        d3.select(this)
                          .attr('width', 8)
                          .attr('height', 8)
                      })
                      .attr('x', function (d, i) {
                        return (i * 10) % 1000 + 1
                      })
                      .attr('y', function (d, i) {
                        return parseInt(i / 100) * 10 + 1
                      })
                      .attr('width', 8)
                      .attr('height', 8)
                      .attr('fill', function (d, i) {
                        if (self.user.profile.try_list.indexOf(d) !== -1) {
                          return 'red'
                        }
                        if (self.user.profile.ac_list.indexOf(d) !== -1) {
                          return 'green'
                        }
                        return 'rgba(238, 238, 238, 0.8)'
                      })
    NProgress.done()
  },
  components: {
    NaN
  }
}
</script>

<style lang='less'>
@code-font: Consolas, Courier New;

.po-userdetails {
  .container {
    padding-left: 0px;
    padding-right: 0px;
  }

  .user-details-bordered {
    border-left-width: 3px;
    border-left-style: solid;
    border-left-color: green;
    padding-left: 20px;
    font-family: @code-font;
    font-size: 16px;
  }

  .user-details-label {
    font-size: 16px;
    font-family: @code-font;
    color: green;
    font-weight: 700;
  }

  #chart-submit-status {
    margin-top: 50px;
  }

  #chart-problem-status {
    font-family: @code-font;
    font-size: 16px;
  }

  .svg-chart-problem-status {
    background-color: white;
    cursor: pointer;
  }
}

</style>

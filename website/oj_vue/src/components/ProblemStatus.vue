<template>
  <div class="po-problem-status">
    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <h2>{{ problem.title }}</h2>
          <hr/>         
        </div>
      </div>
      <div class="row">
        <div class="col-md-6">
          <canvas id='problem-submition-status' width='1000' height='500'></canvas>
        </div>
        <div class="col-md-6">
          <canvas id='problem-language-status' width='1000' height='700'></canvas>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
          <canvas id='problem-day-attention' width='1000' height='300'></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var NProgress = window.NProgress
var Chart = require('chart.js')
export default {
  name: 'ProblemStatus',
  data () {
    return {
      problem: {},
      chart_submit_status: null,
      chart_language_status: null,
      chart_day_attention: null
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      let self = this
      let pid = this.$route.params.pid
      window.fetch(`/api/question/status/${pid}/?format=json`, {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        if (data.success) {
          data = self.trim_data(data)
          transition.next({
            problem: data.question
          })
        }
      }).catch(function (error) {
        NProgress.done()
        console.log(`Error happned: /api/problem/status/${pid}/ =>`, error)
      })
    }
  },
  methods: {
    trim_data: function (data) {
      return data
    }
  },
  ready: function () {
    let self = this
    // Draw submit status chart
    Chart.defaults.global.defaultFontFamily = 'Consolas, Courier New'
    Chart.defaults.global.defaultFontSize = 14
    Chart.defaults.global.animation.duration = 3000
    let ctx_chart_submit_status = document.getElementById('problem-submition-status')
    this.chart_submit_status = new Chart(ctx_chart_submit_status, {
      type: 'bar',
      data: {
        labels: ['AC', 'CE', 'WA', 'RE', 'TLE', 'MLE', 'OLE', 'PE', 'SE'],
        datasets: [{
          label: self.problem.title,
          backgroundColor: 'rgba(231, 84, 64, 0.6)',
          borderColor: 'rgba(255,99,132,1)',
          borderWidth: 0,
          hoverBackgroundColor: 'rgba(231, 84, 64, 0.8)',
          hoverBorderColor: 'rgba(231, 84, 64, 0.8)',
          data: self.problem.status_list
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

    // Draw language status chart
    let ctx_chart_language_status = document.getElementById('problem-language-status')
    this.chart_language_status = new Chart(ctx_chart_language_status, {
      type: 'radar',
      data: {
        labels: ['C', 'C++', 'Java', 'Python2', 'Python3'],
        datasets: [{
          data: self.problem.language_list,
          label: self.problem.title,
          backgroundColor: 'rgba(15, 127, 18, 0.7)',
          borderColor: 'rgba(255,99,132,0)',
          hoverBackgroundColor: 'rgba(15, 127, 18, 1)'
        }]
      }
    })

    // Draw day attention chart
    let ctx_chart_day_attention = document.getElementById('problem-day-attention')
    this.chart_day_attention = new Chart(ctx_chart_day_attention, {
      type: 'line',
      data: {
        labels: self.problem.attention_days,
        datasets: [{
          data: self.problem.attention_values,
          label: self.problem.title,
          backgroundColor: 'rgba(40, 154, 216, 0.6)'
        }]
      }
    })
    NProgress.done()
  },
  components: {}
}
</script>

<style lang='less'>

.po-problem-status {
  #problem-language-status {
  }

  #problem-submition-status {
    margin-top: 90px;
  }

  #problem-day-attention {
    margin-top: 50px;
  }
}

</style>

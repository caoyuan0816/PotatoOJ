<template>
  <div class="po-problem-list">
    <div class="container">
      <ul>
        <template v-for="problem in problems">
          <li class="row">
            <div 
              class="col-md-6 col-sm-6 col-xs-12 problem-title"
              v-bind:class="[isNaN(ac_list) ? borderRed : (ac_list.indexOf(problem.id) !== -1 ? borderGreen : borderRed)]">

              <a v-link="{ path: '/problem/' + problem.id }">
                {{ problem.title }} 
              </a>
              <br/>
              <span class="sub-title">
                #{{ problem.id }} - Source: {{ problem.source }}
              </span>
            </div>
            <div class="col-md-2 col-sm-3 hidden-xs problem-statistic">
              <div class="col-md-6 col-sm-6 problem-statistic-content">
                <a v-link="{ path: '/problem/status/' + problem.id }">
                  {{ problem.ac_num === 0 ? '-' : problem.ac_num }}
                </a>
                <br/>
                <span class="sub-title">
                  ACCEPT
                </span>
              </div>
              <div class="col-md-6 col-sm-6 problem-statistic-content">
                <a v-link="{ path: '/problem/status/' + problem.id }">
                  {{ problem.submit_num === 0 ? '-' : problem.submit_num }}
                </a>
                <br/>
                <span class="sub-title">
                  SUBMIT
                </span>
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
  name: 'ProblemList',
  data () {
    return {
      title: 'Problem List:',
      borderRed: 'border-red',
      borderGreen: 'border-green',
      problems: [
        // currently format:
        // {id: 1, title: 'A+B Problem', source: 'ACM-ICPC'
        //  status: true | false, ac: 10, submit: 101},
      ],
      ac_list: NaN
        // the accpted questions id list
    }
  },
  methods: {
    getBorderColor: function () {
      return 'borderRed'
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      window.fetch('/api/question/?format=json', {
        credentials: 'include'
      }).then(function (response) {
        return response.json()
      }).then(function (data) {
        // Get data success
        if (data.success) {
          transition.next({
            problems: data.questions,
            ac_list: data.ac_list
          })
        } else {
          console.log('get question data failed')
          console.log(data.detail)
        }
        // console.log(data)
        NProgress.done()
      }).catch(function (error) {
        // Error happend
        NProgress.done()
        console.log('Error happend: /api/question/ =>', error)
      })
    },
    activate: function (transition) {
      transition.next()
    },
    deactivate: function (transition) {
      transition.next()
    }
  }
}
</script>

<style lang='less'>

@content-padding:5px;
@border-width: 3px;

.po-problem-list {

  ul {
    padding-left: 0px;
    padding-right: 0px;
  }

  li {
    list-style-type: none;

    margin-left: 0px;
    margin-right: 0px;
    padding-top: @content-padding;
    padding-bottom: @content-padding;

    .border-red{
      border-left-width: @border-width;
      border-left-color: #E75440;
      border-left-style: solid;
    }

    .border-green{
      border-left-width: @border-width;
      border-left-color: green;
      border-left-style: solid;
    }

    a {
      font-size: 18px;
      line-height: 22px;
    }

    .sub-title{
      font-size: 12px;
      line-height: 1px;
      color:#777;
    }

    .problem-statistic {
      text-align: center;
    }
  }
}
</style>

require('../static/font/font.css')
require('../static/bootstrap/css/bootstrap.min.css')
require('../static/nprogress/nprogress.css')
require('../static/codemirror/codemirror.css')
require('../static/codemirror/addon/dialog/dialog.css')
require('../node_modules/codemirror/addon/search/matchesonscrollbar.css')
require('../static/codemirror/theme/neo.css')
require('../node_modules/highlight.js/styles/github-gist.css')

import Vue from 'vue'
import VueRouter from 'vue-router'
import VueValidator from 'vue-validator'

Vue.use(VueRouter)
Vue.use(VueValidator)

var vue_root = Vue.extend(require('./App.vue'))
var router = new VueRouter({
  history: true,
  saveScrollPosition: true
})

router.map({
  '/': {
    component: require('./components/Hello.vue')
  },
  '/problemlist': {
    component: require('./components/ProblemList.vue')
  },
  '/problem/:pid': {
    component: require('./components/ProblemDetials.vue')
  },
  '/statuslist/': {
    component: require('./components/StatusList.vue')
  },
  '/contestlist/': {
    component: require('./components/ContestList.vue')
  },
  '/contest/:cid': {
    component: require('./components/ContestDetails.vue')
  },
  '/ranklist': {
    component: require('./components/Ranklist.vue')
  },
  '/user/:uid': {
    component: require('./components/UserDetails.vue')
  },
  '/status/:sid': {
    component: require('./components/StatusDetails.vue')
  },
  '/problem/status/:pid': {
    component: require('./components/ProblemStatus.vue')
  },
  '/contest/:cid/ranklist': {
    component: require('./components/ContestRankList.vue')
  },
  '/contest/:cid/status/:sid': {
    component: require('./components/ContestStatusDetails.vue')
  }
})

router.start(vue_root, '#entry')

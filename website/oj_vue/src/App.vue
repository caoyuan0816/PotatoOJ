<template>
<div id="app">
	<div class="container-fluid" id="app-container">
		<div id="po-header">
			<po-navbar v-ref:navbar></po-navbar>	
		</div>
		<div id="po-body">
			<router-view transition="fade" transition-mode="out-in">
  			</router-view>
		</div>
		<div id="po-footer">
			<po-footbar></po-footbar>
		</div>
	</div>
</div>
</template>

<script>
import Navbar from './components/Navbar'
import Footbar from './components/Footbar'
// import { alert } from 'vue-strap'

export default {
  components: {
    'po-navbar': Navbar,
    'po-footbar': Footbar
  }
}
</script>

<style lang='less'>

body {
    font-family: Microsoft Yahei, Hiragino Sans GB, Microsoft Sans Serif, WenQuanYi Micro Hei, sans-serif;
	/*background: url("./assets/fill.png") repeat 0 0;*/
}

#app {
	#app-container {
		padding-left: 0px;
		padding-right: 0px;
	}
}

#po-body {
    margin-top: 50px;
}

.fade-transition {
  	transition: opacity 0.9s ease;
}
.fade-enter {
  	opacity: 0;
}
.fade-leave {
	opacity: 0;
}
</style>


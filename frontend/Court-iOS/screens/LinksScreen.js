import React from 'react';
import { Button, ScrollView, StyleSheet } from 'react-native';
import { withNavigation } from 'react-navigation';
import { ExpoLinksView } from '@expo/samples';


class LinksScreen extends React.Component {
  static navigationOptions = {
    title: 'Links',
  };

  render() {
    return (
      <ScrollView style={styles.container}>
        {/* Go ahead and delete ExpoLinksView and replace it with your
           * content, we just wanted to provide you with some helpful links */}
        <ExpoLinksView />
        <Button onPress={() => this.props.navigation.navigate('Auth')} title="Logout" />

      </ScrollView>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 15,
    backgroundColor: '#fff',
  },
});

export default withNavigation(LinksScreen);

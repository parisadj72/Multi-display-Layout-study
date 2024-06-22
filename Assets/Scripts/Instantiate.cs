using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Instantiate : MonoBehaviour
{
    public GameObject InstantiatePrefab;
    public Transform location;
    private void Awake()
    {
        
        Instantiate(InstantiatePrefab, new Vector3(0,0,0), Quaternion.identity);
    }
}
